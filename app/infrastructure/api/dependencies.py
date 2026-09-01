from typing import Awaitable, Callable, Set

from fastapi import Request
from langchain_core.runnables import Runnable
from langgraph.graph.state import CompiledStateGraph

from app.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_trip_suggestion_chain(request: Request) -> Runnable:
    return request.app.state.trip_suggestion_chain


def get_advisor_graph(request: Request) -> CompiledStateGraph:
    return request.app.state.advisor_graph


def get_chat_chain(request: Request) -> Runnable:
    return request.app.state.chat_chain


def get_known_chat_sessions(request: Request) -> Set[str]:
    return request.app.state.known_chat_sessions


def get_insurance_answer(request: Request) -> Callable[[str], Awaitable[str]]:
    return request.app.state.insurance_answer
