import json
from pathlib import Path
from unittest.mock import patch

import pytest

from copthief.reporting.draft_email import main, save_draft_email


def test_save_draft_email_writes_eml_without_network(tmp_path):
    report = {"totals": {"cop": 1, "thief": 2}}
    output_path = tmp_path / "draft.eml"

    result_path = save_draft_email(report, "grader@example.com", str(output_path))

    content = result_path.read_text(encoding="utf-8")
    assert "grader@example.com" in content
    assert "Cop/Thief game_report" in content
    assert '"cop": 1' in content


def test_main_raises_when_report_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        main()


def test_main_writes_draft_from_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("results").mkdir()
    Path("results/game_report.json").write_text(
        json.dumps({"group_name": "SMNGRP05", "totals": {"cop": 90}}), encoding="utf-8"
    )
    with patch("copthief.reporting.draft_email.load_game_config") as cfg:
        cfg.return_value.report_recipient = "grader@example.com"
        main()
    assert Path("results/draft_email.eml").exists()
