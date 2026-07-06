import json
from unittest.mock import patch

import pytest

from copthief.reporting.send_report import send_game_report


def test_send_game_report_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        send_game_report(str(tmp_path / "missing.json"))


def test_send_game_report_delegates_to_gmail_sender(tmp_path):
    report = {"group_name": "SMNGRP05", "totals": {"cop": 90, "thief": 40}}
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    with patch("copthief.reporting.send_report.GmailSender") as mock_sender_cls:
        mock_sender_cls.return_value.send_report.return_value = {"id": "msg-123"}
        response = send_game_report(str(path))

    assert response == {"id": "msg-123"}
    sent_report = mock_sender_cls.return_value.send_report.call_args.args[0]
    assert sent_report["group_name"] == "SMNGRP05"
    recipient = mock_sender_cls.return_value.send_report.call_args.kwargs["recipient"]
    assert recipient == "rmisegal+uoh26b@gmail.com"


def test_main_prints_message_id(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "game_report.json").write_text(
        json.dumps({"group_name": "SMNGRP05", "totals": {}}), encoding="utf-8"
    )
    from copthief.reporting import send_report as module

    monkeypatch.setattr("sys.argv", ["send_report"])
    with patch.object(module, "GmailSender") as sender:
        sender.return_value.send_report.return_value = {"id": "abc999"}
        module.main()
    assert "abc999" in capsys.readouterr().out
