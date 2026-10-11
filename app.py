import os
import subprocess
import threading
import time
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI(title="Academia MCP Proxy")

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

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_backend, daemon=True)
    thread.start()
    time.sleep(3)  # Give the backend server a moment to spin up

@app.get("/")
def root_health_check():
    return {"status": "healthy", "service": "academia_mcp", "transport": "streamable-http"}

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, path_name: str):
    backend_url = f"http://127.0.0.1:{BACKEND_PORT}/{path_name}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        req_content = await request.body()
        response = await client.request(
            method=request.method,
            url=backend_url,
            headers=dict(request.headers),
            params=request.query_params,
            content=req_content,
        )
        return StreamingResponse(
            response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
