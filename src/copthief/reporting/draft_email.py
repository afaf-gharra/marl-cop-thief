"""Builds a draft submission email (.eml) from the game report — network-free, never sends.

Usage: uv run python -m copthief.reporting.draft_email
"""
import json
from pathlib import Path

from copthief.reporting.gmail_sender import build_mime_message
from copthief.shared.config import load_game_config


def save_draft_email(report: dict, recipient: str, output_path: str) -> Path:
    """Write the report as a standard .eml file for human review — no Gmail API call is made."""
    message = build_mime_message(report, recipient, subject="Cop/Thief game_report")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(message.as_bytes())
    return path


def main() -> None:
    config = load_game_config()
    report_path = Path("results/game_report.json")
    if not report_path.exists():
        raise FileNotFoundError("results/game_report.json not found — run `uv run python -m copthief.main` first.")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    output_path = save_draft_email(report, config.report_recipient, "results/draft_email.eml")
    print(f"Draft email saved to {output_path} (NOT sent). Review it, then send manually via")
    print("GmailSender.send_report(...) once GMAIL_CREDENTIALS_PATH is configured.")


if __name__ == "__main__":
    main()
