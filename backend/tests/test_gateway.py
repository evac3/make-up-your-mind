"""Tests for the AI Gateway (/chat endpoint).

The DB service and Gemini SDK are both mocked so these tests run with no
network access and no GEMINI_API_KEY.
"""
from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Minimal stub for the google.genai module so importing main.py never fails
# even when the real SDK is not installed in the test environment.
# ---------------------------------------------------------------------------
def _make_genai_stub():
    genai = types.ModuleType("google.genai")
    google = types.ModuleType("google")
    google.genai = genai
    sys.modules.setdefault("google", google)
    sys.modules.setdefault("google.genai", genai)

    fake_client_cls = MagicMock()
    genai.Client = fake_client_cls
    return genai


_make_genai_stub()

import main as gateway_main  # noqa: E402  (must come after stub)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
FAKE_USER = {
    "id": 1,
    "name": "Alex",
    "condition": "anxiety",
    "about_me": "College student",
    "concerns": "Making wrong choices",
}
FAKE_HISTORY = {"decisions": []}
FAKE_DECISION = {
    "id": 42,
    "message": "Should I drop this class?",
    "ai_response": "Here is my advice.",
    "outcome": None,
    "timestamp": "2026-01-01T00:00:00",
}
FAKE_EVIDENCE = [{"id": 1, "title": "Housing costs", "source": "public_dataset.parquet#1"}]

BASE_PAYLOAD = {
    "user_id": 1,
    "message": "Should I drop this class?",
    "condition": "anxiety",
    "about_me": "College student",
    "concerns": "Making wrong choices",
}


def _mock_response(json_data, status_code=200):
    """Build a minimal requests.Response-like mock."""
    m = MagicMock()
    m.status_code = status_code
    m.json.return_value = json_data
    m.raise_for_status = MagicMock()
    return m


def _db_side_effect(url, **kwargs):
    """Route fake DB responses by URL pattern."""
    if "/user/" in url:
        return _mock_response(FAKE_USER)
    if "/history/" in url:
        return _mock_response(FAKE_HISTORY)
    if "/evidence" in url:
        return _mock_response(FAKE_EVIDENCE)
    if "/decision" in url:
        return _mock_response(FAKE_DECISION)
    return _mock_response({}, 404)


def _db_post_side_effect(url, **kwargs):
    if "/decision" in url:
        return _mock_response(FAKE_DECISION)
    return _mock_response({}, 404)


@pytest.fixture()
def client():
    with TestClient(gateway_main.app) as c:
        yield c


@pytest.fixture()
def mock_gemini():
    """Patch the module-level Gemini client used by main.py."""
    fake_response = MagicMock()
    fake_response.text = "Here is my advice."
    gateway_main.client.models.generate_content.return_value = fake_response
    return gateway_main.client


# ---------------------------------------------------------------------------
# Health / root endpoints
# ---------------------------------------------------------------------------
def test_root(client):
    assert client.get("/").json()["status"] == "running"


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /chat — happy path with all 4 condition branches
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("condition,keyword", [
    ("anxiety disorder", "anxiety"),
    ("ocd diagnosis", "ocd"),
    ("memory loss", "memory"),
    ("general stress", "general"),
])
def test_chat_condition_routing(client, mock_gemini, condition, keyword):
    with patch("main.requests.get", side_effect=_db_side_effect), \
         patch("main.requests.post", side_effect=_db_post_side_effect):
        payload = {**BASE_PAYLOAD, "condition": condition}
        resp = client.post("/chat", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["response"] == "Here is my advice."
    assert body["decision_id"] == 42


def test_chat_returns_decision_id(client, mock_gemini):
    with patch("main.requests.get", side_effect=_db_side_effect), \
         patch("main.requests.post", side_effect=_db_post_side_effect):
        resp = client.post("/chat", json=BASE_PAYLOAD)

    assert resp.status_code == 200
    assert resp.json()["decision_id"] == 42


# ---------------------------------------------------------------------------
# /chat — failure modes
# ---------------------------------------------------------------------------
def test_chat_db_down_returns_503(client, mock_gemini):
    import requests as req_lib
    with patch("main.requests.get", side_effect=req_lib.RequestException("timeout")):
        resp = client.post("/chat", json=BASE_PAYLOAD)

    assert resp.status_code == 503
    assert "8001" in resp.json()["detail"]


def test_chat_evidence_failure_is_silent(client, mock_gemini):
    """Evidence fetch failing should NOT prevent the chat from succeeding."""
    import requests as req_lib

    def db_side_effect_no_evidence(url, **kwargs):
        if "/evidence" in url:
            raise req_lib.RequestException("evidence down")
        return _db_side_effect(url, **kwargs)

    with patch("main.requests.get", side_effect=db_side_effect_no_evidence), \
         patch("main.requests.post", side_effect=_db_post_side_effect):
        resp = client.post("/chat", json=BASE_PAYLOAD)

    assert resp.status_code == 200


def test_chat_decision_save_failure_returns_503(client, mock_gemini):
    import requests as req_lib

    with patch("main.requests.get", side_effect=_db_side_effect), \
         patch("main.requests.post", side_effect=req_lib.RequestException("db write failed")):
        resp = client.post("/chat", json=BASE_PAYLOAD)

    assert resp.status_code == 503
    assert "decision" in resp.json()["detail"].lower()
