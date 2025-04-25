from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from chatter.dependencies import get_assistant_service
from chatter.services.assistant import AssistantService
from chatter.services.event_handler import EventHandler

router = APIRouter()


@router.get("/assistant")
async def get_assistant(assistant: AssistantService = Depends(get_assistant_service)):
    return await assistant.get_assistant()


@router.post("/assistant/threads")
async def post_thread(assistant: AssistantService = Depends(get_assistant_service)):
    thread = await assistant.create_thread()

    return {"data": thread}


class Query(BaseModel):
    text: str
    thread_id: str


@router.post("/assistant/chat")
async def chat(
    query: Query = Body(...),
    assistant: AssistantService = Depends(get_assistant_service),
):
    thread = await assistant.retrieve_thread(query.thread_id)

    await assistant.create_message(thread.id, query.text)

    stream_it = EventHandler()
    gen = assistant.create_gen(thread, stream_it)
    return StreamingResponse(gen, media_type="text/event-stream")
