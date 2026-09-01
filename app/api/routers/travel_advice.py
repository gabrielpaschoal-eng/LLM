from fastapi import APIRouter, Depends
from langgraph.graph.state import CompiledStateGraph

from app.api.dependencies import get_advisor_graph
from app.api.schemas.travel_advice import TravelAdviceRequest, TravelAdviceResponse

router = APIRouter(tags=["travel-advice"])


@router.post("/travel-advice", response_model=TravelAdviceResponse)
async def create_travel_advice(
    body: TravelAdviceRequest,
    graph: CompiledStateGraph = Depends(get_advisor_graph),
) -> TravelAdviceResponse:
    result = await graph.ainvoke({"query": body.query})
    return TravelAdviceResponse(
        advisor=result["destination"].destination,
        response=result["response"],
    )
