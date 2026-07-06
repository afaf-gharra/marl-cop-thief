import json

from copthief.game.scoring import SubGameScore
from copthief.orchestrator.game_series import SeriesResult
from copthief.orchestrator.sub_game import SubGameRecord, TurnRecord
from copthief.reporting.json_report import (
    build_bonus_game_report,
    build_internal_game_report,
    write_report,
)


def test_build_internal_game_report_schema(small_config):
    record = SubGameRecord(
        outcome="cop_wins",
        turns=[TurnRecord(role="thief", message="hi", action="up", position_after=[0, 1])],
        score=SubGameScore(cop_points=20, thief_points=5),
    )
    result = SeriesResult(sub_games=[record], cop_total=20, thief_total=5)

    report = build_internal_game_report(
        result,
        small_config,
        github_repo="https://github.com/example/repo",
        cop_mcp_url="http://127.0.0.1:8801",
        thief_mcp_url="http://127.0.0.1:8802",
        students=["afaf gharra (208123232)"],
    )

    assert report["group_name"] == "SMNGRP05"
    assert report["totals"] == {"cop": 20, "thief": 5}
    assert report["sub_games"][0]["outcome"] == "cop_wins"
    assert report["sub_games"][0]["transcript"][0]["message"] == "hi"


def test_write_report_creates_file(tmp_path, small_config):
    result = SeriesResult()
    report = build_internal_game_report(
        result, small_config, github_repo="", cop_mcp_url="", thief_mcp_url="", students=[]
    )
    path = tmp_path / "nested" / "report.json"
    write_report(report, str(path))
    assert json.loads(path.read_text(encoding="utf-8"))["group_name"] == "SMNGRP05"


def test_build_bonus_game_report_matches_spec_schema():
    report = build_bonus_game_report(
        group_1="SMNGRP05",
        group_2="Team-Beta",
        repos={"group_1": "https://github.com/afaf-gharra/marl-cop-thief",
               "group_2": "https://github.com/beta/marl-cop-thief"},
        mcp_urls={"group_1_cop": "https://a/cop", "group_1_thief": "https://a/thief",
                  "group_2_cop": "https://b/cop", "group_2_thief": "https://b/thief"},
        students={"group_1": ["afaf gharra (208123232)"], "group_2": ["someone"]},
        sub_games=[{"outcome": "cop_wins"}],
        totals_by_group={"SMNGRP05": 80, "Team-Beta": 60},
        bonus_claim={"SMNGRP05": 10, "Team-Beta": 7},
        mutual_agreement=True,
    )
    assert report["report_type"] == "bonus_game"
    assert report["groups"] == {"group_1": "SMNGRP05", "group_2": "Team-Beta"}
    assert report["mcp_url_group_2_thief"] == "https://b/thief"
    assert report["mutual_agreement"] is True
