from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.infrastructure.api.routers import chat_sessions, health, insurance_queries, trip_suggestions, travel_advice
from app.application.insurance_query import create_insurance_query
from app.application.travel_advisor import create_advisor_graph
from app.application.travel_chat import create_chat_with_memory
from app.application.trip_suggestion import create_trip_suggestion_chain
from app.config import load_settings
from app.infrastructure.claude_chat_model import create_model


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = load_settings()
    model = create_model(settings)

    app.state.settings = settings
    app.state.trip_suggestion_chain = create_trip_suggestion_chain(model)
    app.state.advisor_graph = create_advisor_graph(model)
    app.state.chat_chain = create_chat_with_memory(model)
    app.state.known_chat_sessions = set()
    app.state.insurance_answer = create_insurance_query(model, settings.insurance_pdf_paths)

    yield


app = FastAPI(title="Travel & Insurance API", version="1.0.0", lifespan=lifespan)

_API_PREFIX = "/api/v1"
app.include_router(health.router, prefix=_API_PREFIX)
app.include_router(trip_suggestions.router, prefix=_API_PREFIX)
app.include_router(chat_sessions.router, prefix=_API_PREFIX)
app.include_router(travel_advice.router, prefix=_API_PREFIX)
app.include_router(insurance_queries.router, prefix=_API_PREFIX)


def _error_envelope(code: str, message: str, details: object = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_envelope(code=str(exc.status_code), message=str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_envelope(
            code="422", message="Validation error", details=exc.errors()
        ),
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_envelope(code="500", message="Internal server error"),
    )
