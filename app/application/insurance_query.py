from typing import Awaitable, Callable, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.infrastructure.ai.claude_chat_model import ClaudeSDKChatModel
from app.infrastructure.ai.vector_store import create_pdf_retriever

_insurance_query_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Responda usando exclusivamente o conteúdo fornecido"),
        ("human", "{query}\n\nContexto: \n{context}\n\nResposta:"),
    ]
)


def create_insurance_query(model: ClaudeSDKChatModel, pdf_paths: List[str]) -> Callable[[str], Awaitable[str]]:
    retriever = create_pdf_retriever(pdf_paths)
    chain = _insurance_query_prompt | model | StrOutputParser()

    async def answer(question: str) -> str:
        chunks = await retriever.ainvoke(question)
        context = "\n\n".join(chunk.page_content for chunk in chunks)
        return await chain.ainvoke({"query": question, "context": context})

    return answer
