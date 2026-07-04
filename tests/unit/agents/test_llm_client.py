import pytest

from copthief.agents.llm_client import LlmClient, NoApiKeyError
from copthief.shared.gatekeeper import ApiGatekeeper

_CONFIG = {"services": {"default": {"requests_per_minute": 5, "requests_per_hour": 5,
                                     "concurrent_max": 1, "retry_after_seconds": 0, "max_retries": 1}}}


def test_complete_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = LlmClient(ApiGatekeeper(_CONFIG))
    with pytest.raises(NoApiKeyError):
        client.complete("hello")
