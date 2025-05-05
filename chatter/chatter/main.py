import os
import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from openai import AsyncOpenAI

from chatter.config import settings
from chatter.api import assistant
from chatter.services.event_handler import EventHandler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/", response_class=HTMLResponse)
async def serve_html():
    # Serve the HTML file
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r") as file:
        html_content = file.read()

    headers = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache", "Expires": "0"}

    return HTMLResponse(content=html_content, headers=headers)


@app.get("/stream-assistant")
async def stream_assistant(q: str = "tell me a short story"):
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    thread = await client.beta.threads.create()
    print(f"Thread created: {thread.id} Assistant: {settings.OPENAI_ASSISTANT_ID}")

    message = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=q,
    )
    print(f"Message created: {message.id}. Query: {q}")

    async def gen():
        stream_it = EventHandler(client)

        async def run_stream():
            async with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,
                event_handler=stream_it,
            ) as stream:
                await stream.until_done()

        task = asyncio.create_task(run_stream())
        async for token in stream_it.aiter():
            yield token
        await task

    return StreamingResponse(gen(), media_type="text/event-stream")


app.include_router(assistant.router, prefix=settings.API_PREFIX, tags=["Assistant"])
