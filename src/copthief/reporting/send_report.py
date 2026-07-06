"""Sends the final game report to the course address via the Gmail API — the automated
dispatch required by the exercise (§9). The email body contains ONLY the JSON report.

Usage: uv run python -m copthief.reporting.send_report [path/to/report.json]
"""
import json
import sys
from pathlib import Path

from copthief.reporting.gmail_sender import GmailSender
from copthief.shared.config import load_game_config, load_rate_limits
from copthief.shared.gatekeeper import ApiGatekeeper


def send_game_report(report_path: str = "results/game_report.json") -> dict:
    """Load the report JSON and email it to the configured recipient. Returns the API response."""
    config = load_game_config()
    path = Path(report_path)
    if not path.exists():
        raise FileNotFoundError(f"{report_path} not found — run `uv run python -m copthief.main` first.")

    report = json.loads(path.read_text(encoding="utf-8"))
    sender = GmailSender(ApiGatekeeper(load_rate_limits(), service="gmail"))
    response = sender.send_report(report, recipient=config.report_recipient)
    return response


def main() -> None:
    report_path = sys.argv[1] if len(sys.argv) > 1 else "results/game_report.json"
    response = send_game_report(report_path)
    print(f"Report sent. Gmail message id: {response.get('id')}")


if __name__ == "__main__":
    main()
