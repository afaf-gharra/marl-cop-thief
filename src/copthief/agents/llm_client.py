"""Provider-agnostic LLM wrapper (OpenAI or Anthropic, auto-detected from the environment).

All calls are routed through the ApiGatekeeper; prompt/completion token usage is
accumulated in a module-level UsageTracker for the cost analysis (guidelines §11).
"""
from dataclasses import dataclass, field

from copthief.shared.config import get_env
from copthief.shared.gatekeeper import ApiGatekeeper

OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-haiku-4-5"


class NoApiKeyError(RuntimeError):
    """Raised when no LLM API key is configured — callers should fall back to templates."""


@dataclass
class UsageTracker:
    """Accumulates token usage across all LLM calls in this process."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0
    provider: str = ""
    model: str = ""
    _log: list[dict] = field(default_factory=list)

    def record(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.calls += 1
        self._log.append({"prompt": prompt_tokens, "completion": completion_tokens})

    def summary(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }


usage_tracker = UsageTracker()


class LlmClient:
    """Generates one free-text reply per call, gated by the shared rate limiter."""

    def __init__(self, gatekeeper: ApiGatekeeper, model: str | None = None):
        self._gatekeeper = gatekeeper
        self._model = model

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        openai_key = get_env("OPENAI_API_KEY")
        anthropic_key = get_env("ANTHROPIC_API_KEY")
        if openai_key:
            return self._gatekeeper.execute(self._call_openai, openai_key, prompt, max_tokens)
        if anthropic_key:
            return self._gatekeeper.execute(self._call_anthropic, anthropic_key, prompt, max_tokens)
        raise NoApiKeyError("Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY is set; use the offline fallback.")

    def _call_openai(self, api_key: str, prompt: str, max_tokens: int) -> str:
        import openai

        model = self._model or OPENAI_MODEL
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        usage_tracker.provider, usage_tracker.model = "openai", model
        if response.usage:
            usage_tracker.record(response.usage.prompt_tokens, response.usage.completion_tokens)
        return response.choices[0].message.content or ""

    def _call_anthropic(self, api_key: str, prompt: str, max_tokens: int) -> str:
        import anthropic

        model = self._model or ANTHROPIC_MODEL
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        usage_tracker.provider, usage_tracker.model = "anthropic", model
        usage_tracker.record(response.usage.input_tokens, response.usage.output_tokens)
        return response.content[0].text
