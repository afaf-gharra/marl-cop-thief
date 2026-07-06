from unittest.mock import MagicMock, patch

import pytest

from copthief.agents.llm_client import LlmClient, NoApiKeyError, UsageTracker
from copthief.shared.gatekeeper import ApiGatekeeper

_CONFIG = {"services": {"default": {"requests_per_minute": 5, "requests_per_hour": 5,
                                     "concurrent_max": 1, "retry_after_seconds": 0, "max_retries": 1}}}


def _client() -> LlmClient:
    return LlmClient(ApiGatekeeper(_CONFIG))


def test_complete_raises_without_any_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(NoApiKeyError):
        _client().complete("hello")


def test_complete_prefers_openai_when_key_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = _client()
    with patch.object(LlmClient, "_call_openai", return_value="from openai") as mock_call:
        assert client.complete("hi") == "from openai"
    mock_call.assert_called_once()


def test_complete_uses_anthropic_when_only_anthropic_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    client = _client()
    with patch.object(LlmClient, "_call_anthropic", return_value="from anthropic") as mock_call:
        assert client.complete("hi") == "from anthropic"
    mock_call.assert_called_once()


def test_openai_call_records_usage(monkeypatch):
    fake_openai = MagicMock()
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="reply"))]
    fake_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
    fake_openai.OpenAI.return_value.chat.completions.create.return_value = fake_response

    client = _client()
    with patch.dict("sys.modules", {"openai": fake_openai}):
        from copthief.agents import llm_client as module

        before = module.usage_tracker.prompt_tokens
        result = client._call_openai("key", "prompt", 100)

    assert result == "reply"
    assert module.usage_tracker.prompt_tokens == before + 10


def test_usage_tracker_summary():
    tracker = UsageTracker()
    tracker.provider, tracker.model = "openai", "gpt-4o-mini"
    tracker.record(100, 40)
    tracker.record(50, 20)
    summary = tracker.summary()
    assert summary == {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "calls": 2,
        "prompt_tokens": 150,
        "completion_tokens": 60,
    }
