from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.sse import EventSourceResponse

from server.schemas.chat import ChatRequestBody
from server.services.runner import stream_rag_events

router = APIRouter()


@router.post("/runs/stream", response_class=EventSourceResponse)
async def runs_stream(body: ChatRequestBody) -> AsyncIterator[object]:
    """SSE — mỗi sự kiện là JSON một `AgentEvent` (data field)."""
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages is required and non-empty")
    if not any(m.role == "user" and m.content.strip() for m in body.messages):
        raise HTTPException(
            status_code=400,
            detail="At least one user message with non-empty content is required",
        )

    async for ev in stream_rag_events(
        messages=body.messages,
        thread_id=body.threadId,
    ):
        yield ev
