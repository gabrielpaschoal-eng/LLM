import asyncio

from app.application.travel_chat import create_chat_with_memory
from tests.fakes import FakeChatModel


def test_chat_keeps_history_across_turns() -> None:
    chain = create_chat_with_memory(FakeChatModel())
    config = {"configurable": {"session_id": "test-session"}}

    first_reply = asyncio.run(chain.ainvoke({"query": "Oi, quero viajar"}, config=config))
    second_reply = asyncio.run(chain.ainvoke({"query": "E o que mais?"}, config=config))

    assert first_reply
    assert second_reply
    history = chain.get_session_history("test-session")
    assert len(history.messages) == 4
