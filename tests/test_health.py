
from pathlib import Path

from fastapi.testclient import TestClient

import backend.main as main
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


def test_chat_rejects_empty_message():
    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_health_reports_selected_provider(monkeypatch):
    monkeypatch.setattr(main, "MODEL_PROVIDER", "ollama")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["provider"] == "ollama"
    assert response.json()["model"] == main.CHAT_MODEL


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(main, "MODEL_PROVIDER", "openai")
    monkeypatch.setattr(main, "OPENAI_API_KEY", "")

    response = client.post(
        "/artifact",
        json={"prompt": "Create a launch brief", "format": "markdown"},
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_artifact_generation_can_be_mocked(monkeypatch):
    async def fake_generate_text(prompt, max_tokens):
        assert "complete HTML document" in prompt
        assert max_tokens == 2200
        return "<html><body><h1>Preview</h1></body></html>"

    monkeypatch.setattr(main, "MODEL_PROVIDER", "ollama")
    monkeypatch.setattr(main, "generate_text", fake_generate_text)

    response = client.post(
        "/artifact",
        json={"prompt": "Create a launch brief", "format": "html"},
    )

    assert response.status_code == 200
    assert response.json()["format"] == "html"
    assert "<h1>Preview</h1>" in response.json()["content"]


def test_openai_provider_selects_mocked_cloud_generator(monkeypatch):
    async def fake_generate_with_openai(prompt, max_tokens):
        assert max_tokens == 2200
        return "# Cloud-generated artifact"

    monkeypatch.setattr(main, "MODEL_PROVIDER", "openai")
    monkeypatch.setattr(main, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(main, "generate_with_openai", fake_generate_with_openai)

    response = client.post(
        "/artifact",
        json={"prompt": "Create a product brief", "format": "markdown"},
    )

    assert response.status_code == 200
    assert response.json()["model"] == main.OPENAI_MODEL
    assert response.json()["content"] == "# Cloud-generated artifact"


def test_essay_prompt_targets_1250_words_and_keeps_local_limit(monkeypatch):
    async def fake_retrieve_sources(topic):
        return [{"source": "sample.md", "chunk": 2, "text": "Source passage."}]

    async def fake_generate_text(prompt, max_tokens):
        assert "approximately 1,250 words" in prompt
        assert "specific takeaway" in prompt
        assert max_tokens == 1800
        return "# A useful essay\n\n## Takeaway"

    monkeypatch.setattr(main, "MODEL_PROVIDER", "ollama")
    monkeypatch.setattr(main, "retrieve_sources", fake_retrieve_sources)
    monkeypatch.setattr(main, "generate_text", fake_generate_text)

    response = client.post("/write", json={"topic": "Product discovery"})

    assert response.status_code == 200
    assert response.json()["model"] == main.CHAT_MODEL
    assert response.json()["sources"] == [{"source": "sample.md", "chunk": 2}]


def test_artifact_rejects_unknown_format():
    response = client.post(
        "/artifact",
        json={"prompt": "Create a launch brief", "format": "javascript"},
    )

    assert response.status_code == 422


def test_html_artifact_preview_is_sandboxed():
    frontend = Path("frontend/index.html").read_text(encoding="utf-8")

    assert '<iframe id="html-preview"' in frontend
    assert 'sandbox=""' in frontend
    assert "htmlPreview.srcdoc = data.content" in frontend
    assert "innerHTML" not in frontend