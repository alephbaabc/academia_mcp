import os
import uvicorn
from academia_mcp.server import run

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Pass port explicitly so the server binds to Render's required port
    os.environ["PORT"] = str(port)
    run()
