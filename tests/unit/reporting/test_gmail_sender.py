from unittest.mock import MagicMock, patch

import pytest

from copthief.reporting.gmail_sender import GmailNotConfiguredError, GmailSender
from copthief.shared.gatekeeper import ApiGatekeeper

_CONFIG = {"services": {"default": {"requests_per_minute": 5, "requests_per_hour": 5,
                                     "concurrent_max": 1, "retry_after_seconds": 0, "max_retries": 1}}}


def test_send_report_raises_when_not_configured(monkeypatch):
    monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)
    sender = GmailSender(ApiGatekeeper(_CONFIG))
    with pytest.raises(GmailNotConfiguredError):
        sender.send_report({"totals": {}}, recipient="grader@example.com")


def test_send_report_calls_service_when_mocked():
    sender = GmailSender(ApiGatekeeper(_CONFIG))
    fake_service = MagicMock()
    fake_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {"id": "1"}

    with patch.object(GmailSender, "_build_service", return_value=fake_service):
        result = sender.send_report({"totals": {"cop": 1}}, recipient="grader@example.com")

    assert result == {"id": "1"}
    fake_service.users.return_value.messages.return_value.send.assert_called_once()
