import uuid
from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException, Response, status
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from app.infrastructure.api.dependencies import get_chat_chain, get_known_chat_sessions
from app.infrastructure.api.schemas.chat import (
    ChatHistoryMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
)

router = APIRouter(tags=["chat-sessions"])


def _require_known_session(session_id: uuid.UUID, known_sessions: Set[str]) -> str:
    session_key = str(session_id)
    if session_key not in known_sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session_key


@router.post("/chat-sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    response: Response,
    known_sessions: Set[str] = Depends(get_known_chat_sessions),
) -> ChatSessionResponse:
    session_id = uuid.uuid4()
    known_sessions.add(str(session_id))
    response.headers["Location"] = f"/api/v1/chat-sessions/{session_id}"
    return ChatSessionResponse(session_id=session_id)


@router.post(
    "/chat-sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_message(
    session_id: uuid.UUID,
    body: ChatMessageRequest,
    chain: Runnable = Depends(get_chat_chain),
    known_sessions: Set[str] = Depends(get_known_chat_sessions),
) -> ChatMessageResponse:
    session_key = _require_known_session(session_id, known_sessions)
    reply = await chain.ainvoke(
        {"query": body.content}, config={"configurable": {"session_id": session_key}}
    )
    return ChatMessageResponse(role="assistant", content=reply)


@router.get("/chat-sessions/{session_id}/messages", response_model=List[ChatHistoryMessage])
async def list_chat_messages(
    session_id: uuid.UUID,
    chain: Runnable = Depends(get_chat_chain),
    known_sessions: Set[str] = Depends(get_known_chat_sessions),
) -> List[ChatHistoryMessage]:
    session_key = _require_known_session(session_id, known_sessions)
    history = chain.get_session_history(session_key)
    messages = []
    for message in history.messages:
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = "system"
        messages.append(ChatHistoryMessage(role=role, content=str(message.content)))
    return messages
