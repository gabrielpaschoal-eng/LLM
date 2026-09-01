from fastapi import APIRouter, Depends
from langchain_core.runnables import Runnable

from app.infrastructure.api.dependencies import get_trip_suggestion_chain
from app.infrastructure.api.schemas.trip_suggestion import TripSuggestionRequest, TripSuggestionResponse

router = APIRouter(tags=["trip-suggestions"])


@router.post("/trip-suggestions", response_model=TripSuggestionResponse)
async def create_trip_suggestion(
    body: TripSuggestionRequest,
    chain: Runnable = Depends(get_trip_suggestion_chain),
) -> TripSuggestionResponse:
    result = await chain.ainvoke({"interest": body.interest})
    return TripSuggestionResponse(
        destination=result["destination"],
        restaurants=result["restaurants"],
        cultural_activities=result["cultural_activities"],
    )
