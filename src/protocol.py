import json
import socket

def send_message(sock, message):
    sock.sendall(json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n")

def receive_messages(sock):
    buffer = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            return
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            if line.strip():
                yield json.loads(line.decode("utf-8"))
