import os
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import http.client

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
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","service":"academia_mcp"}')
            return
        self.proxy_request("GET")

    def do_POST(self):
        self.proxy_request("POST")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def proxy_request(self, method):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        headers = {key: val for key, val in self.headers.items()}
        headers['Host'] = f"127.0.0.1:{BACKEND_PORT}"
        # Remove hop-by-hop headers
        headers.pop('Transfer-Encoding', None)

        conn = http.client.HTTPConnection("127.0.0.1", BACKEND_PORT, timeout=120)
        try:
            conn.request(method, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            
            self.send_response(resp.status)
            for header, val in resp.getheaders():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, val)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # Stream chunks down instead of blocking
            while True:
                chunk = resp.read(1024)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except Exception as e:
            try:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(str(e).encode())
            except:
                pass
        finally:
            conn.close()

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    thread = threading.Thread(target=start_backend, daemon=True)
    thread.start()
    time.sleep(3)

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)
    server.serve_forever()