from copthief.reporting.bonus_demo import run_bonus_demo


def test_run_bonus_demo_produces_valid_bonus_report(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    report = run_bonus_demo()

    assert report["report_type"] == "bonus_game"
    assert report["groups"]["group_1"] == "SMNGRP05"
    assert set(report["totals_by_group"]) == set(report["bonus_claim"])
    assert report["mutual_agreement"] is True
    # 3+3 split of the configured 6-game series.
    assert len(report["sub_games"]) >= 2
    assert all("matchup" in sg for sg in report["sub_games"])
