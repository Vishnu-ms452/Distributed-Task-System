import argparse
import socket
import time
from protocol import send_message, receive_messages

def calculate(operation, numbers):
    if not numbers: raise ValueError("At least one number is required")
    if operation == "sum": return sum(numbers)
    if operation == "multiply":
        result = 1
        for n in numbers: result *= n
        return result
    if operation == "max": return max(numbers)
    if operation == "min": return min(numbers)
    raise ValueError(f"Unsupported operation: {operation}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True, help="Manager IP; use 127.0.0.1 for same-machine testing")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--id", required=True, dest="worker_id")
    p.add_argument("--reconnect", action="store_true")
    a = p.parse_args()
    while True:
        try:
            print(f"[{a.worker_id}] Connecting to {a.host}:{a.port}...", flush=True)
            with socket.create_connection((a.host, a.port), timeout=10) as sock:
                sock.settimeout(None)
                send_message(sock, {"type": "register", "worker_id": a.worker_id})
                print(f"[{a.worker_id}] Connected.", flush=True)
                for msg in receive_messages(sock):
                    kind = msg.get("type")
                    if kind == "registered":
                        print(f"[{a.worker_id}] Registration confirmed.")
                    elif kind == "task":
                        tid, op, nums = msg["task_id"], msg["operation"], msg["numbers"]
                        print(f"[{a.worker_id}] Received {tid[:8]}: {op} {nums}")
                        try:
                            result = calculate(op, nums)
                            send_message(sock, {"type": "result", "task_id": tid, "ok": True, "result": result})
                            print(f"[{a.worker_id}] Result: {result}")
                        except Exception as exc:
                            send_message(sock, {"type": "result", "task_id": tid, "ok": False, "error": str(exc)})
                    elif kind == "shutdown":
                        return
                    elif kind == "error":
                        print(f"[{a.worker_id}] Manager error: {msg.get('message')}")
            print(f"[{a.worker_id}] Connection closed.")
        except (OSError, ValueError) as exc:
            print(f"[{a.worker_id}] Error: {exc}")
        if not a.reconnect: break
        time.sleep(2)

if __name__ == "__main__":
    main()
