# server_tcp.py
import socket, threading, io
from flask import send_file, abort
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

latest = None
lock = threading.Lock()

# ---------- 1. TCP 线程：收 ESP32 的裸 JPEG ----------
def tcp_receiver():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 5000))
    srv.listen(1)
    while True:
        conn, addr = srv.accept()
        data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        conn.close()
        if data:
            with lock:
                latest = data

threading.Thread(target=tcp_receiver, daemon=True).start()

# ---------- 2. HTTP 线程：给小程序 ----------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/latest.jpg":
            with lock:
                if latest is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                self.wfile.write(latest)
        else:
            self.send_response(404)
            self.end_headers()

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", 5000), Handler).serve_forever(), daemon=True).start()

print("TCP 5000 & HTTP 5000 已启动")