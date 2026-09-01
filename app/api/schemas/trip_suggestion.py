from pydantic import BaseModel, Field


class TripSuggestionRequest(BaseModel):
    interest: str = Field(..., min_length=1, examples=["praias"])


class Destination(BaseModel):
    city: str
    reason: str


class Restaurants(BaseModel):
    city: str
    restaurants: str


class TripSuggestionResponse(BaseModel):
    destination: Destination
    restaurants: Restaurants
    cultural_activities: str
