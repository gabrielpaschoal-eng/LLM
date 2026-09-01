from typing import Literal, TypedDict

from pydantic import BaseModel, Field


class Destination(BaseModel):
    city: str = Field("The recommended city to visit")
    reason: str = Field("Reason why this city is worth visiting")


class Restaurants(BaseModel):
    city: str = Field("The recommended city to visit")
    restaurants: str = Field("Recommended restaurants in the city")


class Route(BaseModel):
    destination: Literal["praia", "montanha"]


class AdvisorState(TypedDict):
    query: str
    destination: Route
    response: str
