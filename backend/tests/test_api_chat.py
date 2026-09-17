from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.rag.retriever import RetrievedChunk

client = TestClient(app)


def test_chat_rejects_empty_question():
    response = client.post("/chat", json={"question": "   "})
    assert response.status_code == 400


@patch("app.api.chat.retrieve_relevant_chunks", return_value=[])
def test_chat_returns_not_found_when_no_chunks_clear_threshold(mock_retrieve):
    response = client.post("/chat", json={"question": "What is the capital of France?"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is False
    assert body["sources"] == []


@patch("app.api.chat.generate_answer", return_value="The exam deadline is 30 June.")
@patch("app.api.chat.retrieve_relevant_chunks")
def test_chat_returns_grounded_answer_with_sources(mock_retrieve, mock_generate):
    mock_retrieve.return_value = [
        RetrievedChunk(
            chunk_id="DOC_001_CHUNK_0001",
            text="Students must submit their identity proof by 30 June.",
            document_id="DOC_001",
            filename="policy.pdf",
            page=8,
            similarity=0.82,
        )
    ]

    response = client.post("/chat", json={"question": "What is the exam deadline?"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["answer"] == "The exam deadline is 30 June."
    assert body["sources"][0]["document"] == "policy.pdf"
    assert body["sources"][0]["page"] == 8


def test_health_endpoint_returns_status():
    with patch("app.api.health.chroma.health_check", return_value=True), patch(
        "app.api.health.metadata.health_check", new_callable=AsyncMock, return_value=True
    ), patch("app.api.health.get_embedding_model", return_value=object()):
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
