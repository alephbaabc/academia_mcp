import os
import asyncio
import uvicorn
from academia_mcp.server import app as mcp_app

# If academia_mcp exposes a Starlette/FastAPI app object directly, we can add a root handler or use it natively.
# Let's add a root route directly to the mcp app if it supports it, or wrap it cleanly:
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    # Check if mcp_app is a FastAPI/Starlette instance
    if hasattr(mcp_app, "get"):
        @mcp_app.get("/")
        async def root():
            return {"status": "healthy", "service": "academia_mcp"}
        app = mcp_app
    else:
        # Fallback wrapper
        app = FastAPI(title="Academia MCP")
        @app.get("/")
        async def root():
            return {"status": "healthy", "service": "academia_mcp"}
except Exception:
    app = mcp_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)