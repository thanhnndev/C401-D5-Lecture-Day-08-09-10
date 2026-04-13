from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequestBody(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)
    threadId: Optional[str] = None
