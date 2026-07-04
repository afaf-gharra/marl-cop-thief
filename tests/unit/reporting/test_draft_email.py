from copthief.reporting.draft_email import save_draft_email


def test_save_draft_email_writes_eml_without_network(tmp_path):
    report = {"totals": {"cop": 1, "thief": 2}}
    output_path = tmp_path / "draft.eml"

    result_path = save_draft_email(report, "grader@example.com", str(output_path))

    content = result_path.read_text(encoding="utf-8")
    assert "grader@example.com" in content
    assert "Cop/Thief game_report" in content
    assert '"cop": 1' in content
