from typing import Awaitable, Callable

from fastapi import APIRouter, Depends

from app.infrastructure.api.dependencies import get_insurance_answer
from app.infrastructure.api.schemas.insurance import InsuranceQueryRequest, InsuranceQueryResponse

router = APIRouter(tags=["insurance-queries"])


@router.post("/insurance-queries", response_model=InsuranceQueryResponse)
async def create_insurance_query(
    body: InsuranceQueryRequest,
    answer: Callable[[str], Awaitable[str]] = Depends(get_insurance_answer),
) -> InsuranceQueryResponse:
    return InsuranceQueryResponse(answer=await answer(body.question))
