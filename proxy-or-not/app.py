import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello")
async def hello():
    return JSONResponse({"message": "Hello from FastAPI API!"})


# Catch-all for any path to serve index.html if file does not exist
@app.get("/{full_path:path}", response_class=FileResponse)
async def serve_react_app(request: Request, full_path: str):
    static_dir = os.path.join(os.path.dirname(__file__), "ui", "dist")
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    # fallback to index.html for client-side routing
    return FileResponse(os.path.join(static_dir, "index.html"))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
