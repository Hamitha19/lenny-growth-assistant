
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "indexed_chunks" in data
    assert data["indexed_chunks"] >= 0


def test_chat_requires_message():
    response = client.post("/chat", json={})

    assert response.status_code == 422