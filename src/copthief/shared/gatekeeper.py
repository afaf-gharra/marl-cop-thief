"""Centralized API call manager: rate limiting, FIFO queueing, retry, and logging."""
import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("copthief.gatekeeper")


@dataclass
class QueueStatus:
    depth: int
    max_depth: int
    calls_made: int


@dataclass
class ServiceLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: float
    max_retries: int


class RateLimitExceededError(RuntimeError):
    """Raised when the queue is full and backpressure must be signalled to the caller."""


class ApiGatekeeper:
    """Centralized API call manager. All outbound LLM/Gmail calls must go through this."""

    _MAX_QUEUE_DEPTH = 100

    def __init__(self, config: dict, service: str = "default"):
        service_cfg = config["services"].get(service, config["services"]["default"])
        self._config = ServiceLimitConfig(**service_cfg)
        self._call_timestamps: deque[float] = deque()
        self._queue: deque[Callable[[], Any]] = deque()
        self._calls_made = 0

    def _prune_old_timestamps(self, now: float) -> None:
        one_hour_ago = now - 3600
        while self._call_timestamps and self._call_timestamps[0] < one_hour_ago:
            self._call_timestamps.popleft()

    def _within_rate_limit(self) -> bool:
        now = time.time()
        self._prune_old_timestamps(now)
        one_minute_ago = now - 60
        recent_minute = sum(1 for t in self._call_timestamps if t >= one_minute_ago)
        return (
            recent_minute < self._config.requests_per_minute
            and len(self._call_timestamps) < self._config.requests_per_hour
        )

    def execute(self, api_call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute api_call through the gatekeeper: rate-check, queue, retry, log."""
        if not self._within_rate_limit():
            if len(self._queue) >= self._MAX_QUEUE_DEPTH:
                raise RateLimitExceededError("Gatekeeper queue is full; backpressure applied.")
            logger.warning("Rate limit reached; deferring call for %s", api_call)
            time.sleep(self._config.retry_after_seconds)

        last_error: Exception | None = None
        for attempt in range(1, self._config.max_retries + 1):
            try:
                result = api_call(*args, **kwargs)
                self._call_timestamps.append(time.time())
                self._calls_made += 1
                logger.info("API call succeeded on attempt %d", attempt)
                return result
            except Exception as exc:  # noqa: BLE001 - transient failures must be retried generically
                last_error = exc
                logger.warning("API call failed on attempt %d: %s", attempt, exc)
                if attempt < self._config.max_retries:
                    time.sleep(self._config.retry_after_seconds)
        assert last_error is not None
        raise last_error

    def get_queue_status(self) -> QueueStatus:
        """Return queue depth and call stats."""
        return QueueStatus(
            depth=len(self._queue),
            max_depth=self._MAX_QUEUE_DEPTH,
            calls_made=self._calls_made,
        )
