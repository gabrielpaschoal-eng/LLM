from typing import Dict

from langchain.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.infrastructure.claude_chat_model import ClaudeSDKChatModel

_suggestion_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um guia de viagem especializado em destinos brasileiros. Apresente-se como Sr. Passeios"),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
    ]
)


def create_chat_with_memory(model: ClaudeSDKChatModel) -> Runnable:
    chain = _suggestion_prompt | model | StrOutputParser()
    memory: Dict[str, InMemoryChatMessageHistory] = {}

    def history_by_session(session: str) -> InMemoryChatMessageHistory:
        if session not in memory:
            memory[session] = InMemoryChatMessageHistory()
        return memory[session]

    return RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=history_by_session,
        input_messages_key="query",
        history_messages_key="chat_history",
    )
