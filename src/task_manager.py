import argparse
import queue
import socket
import threading
import time
import uuid
from protocol import send_message, receive_messages

class TaskManager:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.lock = threading.RLock()
        self.workers = {}
        self.tasks = {}
        self.pending = queue.Queue()
        self.stopping = threading.Event()

    def log(self, text):
        print(f"\\n[manager] {text}", flush=True)

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.server.settimeout(1)
        self.log(f"Listening on {self.host}:{self.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()
        print("Commands: add <sum|multiply|max|min> <numbers...> | workers | tasks | help | quit")
        try:
            while True:
                line = input("manager> ").strip()
                if not line:
                    continue
                parts = line.split()
                cmd = parts[0].lower()
                if cmd == "quit":
                    break
                elif cmd == "workers":
                    with self.lock:
                        if not self.workers: print("No workers connected.")
                        for wid, w in self.workers.items():
                            print(f"{wid}: {'busy' if w['busy'] else 'idle'} from {w['address']}")
                elif cmd == "tasks":
                    with self.lock:
                        if not self.tasks: print("No tasks submitted.")
                        for tid, t in self.tasks.items():
                            print(f"{tid[:8]} {t['operation']} {t['numbers']} status={t['status']} worker={t['worker'] or '-'} result={t.get('result')!r} error={t.get('error') or ''}")
                elif cmd == "help":
                    print("add sum 1 2 3 | add multiply 2 3 4 | workers | tasks | quit")
                elif cmd == "add" and len(parts) >= 3:
                    op = parts[1].lower()
                    if op not in {"sum", "multiply", "max", "min"}:
                        print("Supported operations: sum, multiply, max, min"); continue
                    try: nums = [float(x) if "." in x else int(x) for x in parts[2:]]
                    except ValueError: print("Provide numbers only."); continue
                    tid = uuid.uuid4().hex
                    with self.lock:
                        self.tasks[tid] = {"operation": op, "numbers": nums, "status": "queued", "worker": None}
                        self.pending.put(tid)
                    self.log(f"Queued task {tid[:8]}: {op} {nums}")
                    self.dispatch()
                else:
                    print("Unknown command. Type help.")
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            self.stopping.set()
            self.server.close()
            with self.lock: workers = list(self.workers.values())
            for w in workers:
                try: send_message(w["sock"], {"type": "shutdown"})
                except OSError: pass
                try: w["sock"].close()
                except OSError: pass
            self.log("Stopped.")

    def accept_loop(self):
        while not self.stopping.is_set():
            try: conn, addr = self.server.accept()
            except socket.timeout: continue
            except OSError: return
            threading.Thread(target=self.worker_loop, args=(conn, addr), daemon=True).start()

    def worker_loop(self, conn, addr):
        worker_id = None
        try:
            for msg in receive_messages(conn):
                if msg.get("type") == "register":
                    worker_id = str(msg.get("worker_id", "")).strip()
                    if not worker_id:
                        send_message(conn, {"type": "error", "message": "worker_id required"}); return
                    with self.lock:
                        old = self.workers.get(worker_id)
                        if old:
                            try: old["sock"].close()
                            except OSError: pass
                        self.workers[worker_id] = {"sock": conn, "address": addr, "busy": None, "send_lock": threading.Lock()}
                    send_message(conn, {"type": "registered", "worker_id": worker_id})
                    self.log(f"Worker {worker_id} connected from {addr}")
                    self.dispatch()
                elif msg.get("type") == "result":
                    tid = msg.get("task_id")
                    with self.lock:
                        task = self.tasks.get(tid)
                        worker = self.workers.get(worker_id)
                        if task and worker and task["status"] == "running" and task["worker"] == worker_id:
                            task["status"] = "completed" if msg.get("ok") else "failed"
                            task["result"] = msg.get("result")
                            task["error"] = msg.get("error")
                            worker["busy"] = None
                            self.log(f"Task {tid[:8]} {task['status']} on {worker_id}: {task.get('result', task.get('error'))}")
                    self.dispatch()
                else:
                    send_message(conn, {"type": "error", "message": "unknown message"})
        except (OSError, ValueError) as exc:
            self.log(f"Connection from {addr} ended: {exc}")
        finally:
            with self.lock:
                current = self.workers.get(worker_id) if worker_id else None
                if current and current["sock"] is conn:
                    self.workers.pop(worker_id, None)
                    busy = current["busy"]
                    if busy and busy in self.tasks and self.tasks[busy]["status"] == "running":
                        self.tasks[busy]["status"] = "queued"
                        self.tasks[busy]["worker"] = None
                        self.pending.put(busy)
                    self.log(f"Worker {worker_id} disconnected")
            try: conn.close()
            except OSError: pass
            self.dispatch()

    def dispatch(self):
        with self.lock:
            idle = [ (wid, w) for wid, w in self.workers.items() if w["busy"] is None ]
            while idle and not self.pending.empty():
                wid, worker = idle.pop(0)
                try: tid = self.pending.get_nowait()
                except queue.Empty: break
                task = self.tasks.get(tid)
                if not task or task["status"] != "queued": continue
                task["status"], task["worker"] = "running", wid
                worker["busy"] = tid
                try:
                    with worker["send_lock"]:
                        send_message(worker["sock"], {"type": "task", "task_id": tid, "operation": task["operation"], "numbers": task["numbers"]})
                    self.log(f"Assigned task {tid[:8]} to {wid}")
                except OSError:
                    worker["busy"] = None
                    task["status"], task["worker"] = "queued", None
                    self.pending.put(tid)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=5000)
    a = p.parse_args()
    TaskManager(a.host, a.port).start()

if __name__ == "__main__":
    main()
