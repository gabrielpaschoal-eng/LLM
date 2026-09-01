import asyncio

from app.application.travel_advisor import create_advisor_graph
from tests.fakes import FakeChatModel


def test_routes_to_mountain_advisor() -> None:
    graph = create_advisor_graph(FakeChatModel())

    result = asyncio.run(graph.ainvoke({"query": "Quero escalar montanhas radicais"}))

    assert result["destination"].destination == "montanha"
    assert "Sr Montanha" in result["response"]


def test_routes_to_beach_advisor() -> None:
    graph = create_advisor_graph(FakeChatModel())

    result = asyncio.run(graph.ainvoke({"query": "Quero relaxar numa praia tranquila"}))

    assert result["destination"].destination == "praia"
    assert "Sra Praia" in result["response"]
