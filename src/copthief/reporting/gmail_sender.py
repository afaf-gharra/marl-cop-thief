"""Gmail API sender for the final game report. Fully implemented per Google's OAuth quickstart,
routed through the ApiGatekeeper — but real sending requires the user's own OAuth credentials
(see docs/PRD_gmail_reporting.md); this module is unit-tested with a mocked API client only.
"""
import base64
import json
from email.mime.text import MIMEText
from pathlib import Path

from copthief.shared.config import get_env
from copthief.shared.gatekeeper import ApiGatekeeper

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailNotConfiguredError(RuntimeError):
    """Raised when OAuth credentials are missing — this is the expected state until the user
    completes the one-time interactive Google consent flow described in the PRD."""


def build_mime_message(report: dict, recipient: str, subject: str = "Cop/Thief game_report") -> MIMEText:
    """Build the email body without touching the network — reused by both the real sender
    and `scripts/build_draft_email.py`, which only saves a draft for human review."""
    message = MIMEText(json.dumps(report, indent=2, ensure_ascii=False), _subtype="plain")
    message["to"] = recipient
    message["subject"] = subject
    return message


class GmailSender:
    """Sends the internal_game_report JSON as an email body via the Gmail API."""

    def __init__(self, gatekeeper: ApiGatekeeper):
        self._gatekeeper = gatekeeper

    def _build_service(self):
        credentials_path = get_env("GMAIL_CREDENTIALS_PATH")
        token_path = get_env("GMAIL_TOKEN_PATH", "config/.gmail_token.json")
        if not credentials_path or not Path(credentials_path).exists():
            raise GmailNotConfiguredError(
                "GMAIL_CREDENTIALS_PATH is not set or the credentials file is missing. "
                "Run the OAuth setup in docs/PRD_gmail_reporting.md first."
            )

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        if Path(token_path).exists():
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            Path(token_path).write_text(creds.to_json(), encoding="utf-8")
        return build("gmail", "v1", credentials=creds)

    def send_report(self, report: dict, recipient: str, subject: str = "Cop/Thief game_report") -> dict:
        """Send `report` (the internal_game_report dict) as an email body to `recipient`."""

        def _call():
            service = self._build_service()
            message = build_mime_message(report, recipient, subject)
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return service.users().messages().send(userId="me", body={"raw": raw}).execute()

        return self._gatekeeper.execute(_call)
