import uuid

from pydantic import BaseModel, Field


class ChatSessionResponse(BaseModel):
    session_id: uuid.UUID


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    role: str
    content: str


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
