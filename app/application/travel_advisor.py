from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.domain.travel import AdvisorState, Route
from app.infrastructure.ai.claude_chat_model import ClaudeSDKChatModel

_beach_advisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Apresente-se como Sra Praia. Você é uma especialista em viagens com destinoas para praia."),
        ("human", "{query}"),
    ]
)

_mountain_advisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Apresente-se como Sr Montanha. Você é uma especialista em viagens com destinoas para montanhas e atividades radicais."),
        ("human", "{query}"),
    ]
)

_router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Responda apenas com 'praia' ou 'montanha'"),
        ("human", "{query}"),
    ]
)


def _choose_node(state: AdvisorState) -> Literal["praia", "montanha"]:
    return "praia" if state["destination"].destination == "praia" else "montanha"


def create_advisor_graph(model: ClaudeSDKChatModel) -> CompiledStateGraph:
    beach_chain = _beach_advisor_prompt | model | StrOutputParser()
    mountain_chain = _mountain_advisor_prompt | model | StrOutputParser()
    router = _router_prompt | model.with_structured_output(Route)

    async def router_node(state: AdvisorState, config: RunnableConfig) -> dict:
        return {"destination": await router.ainvoke({"query": state["query"]}, config)}

    async def beach_node(state: AdvisorState, config: RunnableConfig) -> dict:
        return {"response": await beach_chain.ainvoke({"query": state["query"]}, config)}

    async def mountain_node(state: AdvisorState, config: RunnableConfig) -> dict:
        return {"response": await mountain_chain.ainvoke({"query": state["query"]}, config)}

    graph = StateGraph(AdvisorState)
    graph.add_node("route", router_node)
    graph.add_node("praia", beach_node)
    graph.add_node("montanha", mountain_node)

    graph.add_edge(START, "route")
    graph.add_conditional_edges("route", _choose_node)
    graph.add_edge("praia", END)
    graph.add_edge("montanha", END)

    return graph.compile()
