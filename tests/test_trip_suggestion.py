import asyncio

from app.application.trip_suggestion import create_trip_suggestion_chain
from tests.fakes import FakeChatModel


def test_trip_suggestion_chain_keeps_all_intermediate_results() -> None:
    chain = create_trip_suggestion_chain(FakeChatModel())

    result = asyncio.run(chain.ainvoke({"interest": "praias"}))

    assert result["destination"]["city"] == "Florianópolis"
    assert result["destination"]["reason"]
    assert result["restaurants"]["city"] == "Florianópolis"
    assert result["restaurants"]["restaurants"]
    assert result["cultural_activities"]
