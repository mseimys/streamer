
import logging
from fastapi import FastAPI

from chatter.config import settings
from chatter.api import assistant

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

@app.get("/", tags=["Root"])
async def health():
    """Check if the API is running"""
    return {"status": "👌"}

app.include_router(assistant.router, prefix=settings.API_PREFIX, tags=["Assistant"])
