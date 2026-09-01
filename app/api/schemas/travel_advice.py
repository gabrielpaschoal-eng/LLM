from typing import Literal

from pydantic import BaseModel, Field


class TravelAdviceRequest(BaseModel):
    query: str = Field(..., min_length=1)


class TravelAdviceResponse(BaseModel):
    advisor: Literal["praia", "montanha"]
    response: str
