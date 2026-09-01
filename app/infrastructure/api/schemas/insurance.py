from pydantic import BaseModel, Field


class InsuranceQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class InsuranceQueryResponse(BaseModel):
    answer: str
