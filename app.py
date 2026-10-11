import os
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

BACKEND_PORT = 10001
backend_process = None

def start_backend():
    global backend_process
    cmd = [
        "uv", "run", "python", "-m", "academia_mcp",
        "--transport", "streamable-http",
        "--port", str(BACKEND_PORT)
    ]
    backend_process = subprocess.Popen(cmd)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","service":"academia_mcp"}')
            return
        self.proxy_request("GET")

    def do_POST(self):
        self.proxy_request("POST")

    def proxy_request(self, method):
        target_url = f"http://127.0.0.1:{BACKEND_PORT}{self.path}"
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        headers = {key: val for key, val in self.headers.items()}
        
        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for header, val in resp.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, val)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    thread = threading.Thread(target=start_backend, daemon=True)
    thread.start()
    time.sleep(3)  # Wait for backend to spin up

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)
    server.serve_forever()