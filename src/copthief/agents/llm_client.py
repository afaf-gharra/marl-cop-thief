"""Thin Anthropic API wrapper. All calls are routed through the ApiGatekeeper."""
from copthief.shared.config import get_env
from copthief.shared.gatekeeper import ApiGatekeeper

DEFAULT_MODEL = "claude-haiku-4-5"


class NoApiKeyError(RuntimeError):
    """Raised when no ANTHROPIC_API_KEY is configured — callers should fall back to templates."""


class LlmClient:
    """Generates one free-text reply per call, gated by the shared rate limiter."""

    def __init__(self, gatekeeper: ApiGatekeeper, model: str = DEFAULT_MODEL):
        self._gatekeeper = gatekeeper
        self._model = model

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        api_key = get_env("ANTHROPIC_API_KEY")
        if not api_key:
            raise NoApiKeyError("ANTHROPIC_API_KEY is not set; use the offline template fallback.")

        def _call() -> str:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        return self._gatekeeper.execute(_call)
