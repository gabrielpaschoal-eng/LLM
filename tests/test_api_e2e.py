import pytest
from fastapi.testclient import TestClient

from app.infrastructure.api.main import app
from tests.fakes import FakeChatModel, FakeRetriever


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        "app.infrastructure.api.main.create_model",
        lambda settings: FakeChatModel(),
    )
    monkeypatch.setattr(
        "app.application.insurance_query.create_pdf_retriever",
        lambda pdf_paths: FakeRetriever(),
    )
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_trip_suggestion_flow(client: TestClient) -> None:
    response = client.post("/api/v1/trip-suggestions", json={"interest": "praias"})
    assert response.status_code == 200
    body = response.json()
    assert body["destination"]["city"] == "Florianópolis"
    assert body["restaurants"]["city"] == "Florianópolis"
    assert body["cultural_activities"]


def test_trip_suggestion_rejects_empty_interest(client: TestClient) -> None:
    response = client.post("/api/v1/trip-suggestions", json={"interest": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "422"


def test_chat_session_full_flow(client: TestClient) -> None:
    create_response = client.post("/api/v1/chat-sessions")
    assert create_response.status_code == 201
    session_id = create_response.json()["session_id"]
    assert create_response.headers["location"] == f"/api/v1/chat-sessions/{session_id}"

    first_message = client.post(
        f"/api/v1/chat-sessions/{session_id}/messages", json={"content": "Oi, quero viajar"}
    )
    assert first_message.status_code == 201
    assert first_message.json()["role"] == "assistant"

    second_message = client.post(
        f"/api/v1/chat-sessions/{session_id}/messages", json={"content": "E o que mais?"}
    )
    assert second_message.status_code == 201

    history = client.get(f"/api/v1/chat-sessions/{session_id}/messages")
    assert history.status_code == 200
    assert len(history.json()) == 4


def test_chat_message_unknown_session_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat-sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "oi"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "404"


def test_travel_advice_routes_to_mountain(client: TestClient) -> None:
    response = client.post("/api/v1/travel-advice", json={"query": "Quero escalar montanhas radicais"})
    assert response.status_code == 200
    body = response.json()
    assert body["advisor"] == "montanha"
    assert body["response"]


def test_insurance_query(client: TestClient) -> None:
    response = client.post(
        "/api/v1/insurance-queries", json={"question": "Como funciona a proteção de compra?"}
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "Resposta baseada no contexto fornecido."
