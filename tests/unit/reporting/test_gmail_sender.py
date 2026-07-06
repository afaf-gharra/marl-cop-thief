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


def test_build_service_uses_cached_valid_token(tmp_path, monkeypatch):
    """Exercise the OAuth path with a mocked google stack and a valid cached token."""
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text("{}", encoding="utf-8")
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", str(creds_file))
    monkeypatch.setenv("GMAIL_TOKEN_PATH", str(token_file))

    valid_creds = MagicMock(valid=True)
    google = MagicMock()
    google.oauth2.credentials.Credentials.from_authorized_user_file.return_value = valid_creds
    modules = {
        "google": google,
        "google.auth": google.auth,
        "google.auth.transport": google.auth.transport,
        "google.auth.transport.requests": google.auth.transport.requests,
        "google.oauth2": google.oauth2,
        "google.oauth2.credentials": google.oauth2.credentials,
        "google_auth_oauthlib": MagicMock(),
        "google_auth_oauthlib.flow": MagicMock(),
        "googleapiclient": MagicMock(),
        "googleapiclient.discovery": MagicMock(build=MagicMock(return_value="service")),
    }
    with patch.dict("sys.modules", modules):
        service = GmailSender(ApiGatekeeper(_CONFIG))._build_service()
    assert service is not None
