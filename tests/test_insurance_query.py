import asyncio

from app.application.insurance_query import create_insurance_query
from tests.fakes import FakeChatModel, FakeRetriever


def test_insurance_query_answers_using_retrieved_context(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.application.insurance_query.create_pdf_retriever",
        lambda pdf_paths: FakeRetriever(),
    )

    answer = create_insurance_query(FakeChatModel(), ["fake.pdf"])
    response = asyncio.run(answer("Como funciona a proteção de compra?"))

    assert response == "Resposta baseada no contexto fornecido."
