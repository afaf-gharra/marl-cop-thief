import pytest

from copthief.shared.gatekeeper import ApiGatekeeper

_CONFIG = {
    "services": {
        "default": {
            "requests_per_minute": 30,
            "requests_per_hour": 500,
            "concurrent_max": 5,
            "retry_after_seconds": 0,
            "max_retries": 3,
        }
    }
}


def test_execute_returns_call_result():
    gatekeeper = ApiGatekeeper(_CONFIG)
    assert gatekeeper.execute(lambda: 42) == 42
    assert gatekeeper.get_queue_status().calls_made == 1


def test_execute_retries_then_succeeds():
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("transient")
        return "ok"

    gatekeeper = ApiGatekeeper(_CONFIG)
    assert gatekeeper.execute(flaky) == "ok"
    assert calls["count"] == 2


def test_execute_raises_after_max_retries():
    def always_fails():
        raise RuntimeError("permanent")

    gatekeeper = ApiGatekeeper(_CONFIG)
    with pytest.raises(RuntimeError, match="permanent"):
        gatekeeper.execute(always_fails)
