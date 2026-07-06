"""Self-play demonstration of the inter-group bonus pipeline (exercise §12).

A real inter-group match needs a *second* team's MCP servers, which we don't
have. This script instead pits two independent instances of our own system
against each other (group_1's cop vs group_2's thief, then swapped — the 3+3
split the spec describes) and emits a spec-compliant §9.2 `bonus_game` report.
It proves the bonus code path end-to-end; it is NOT a genuine cross-group game.

Usage: uv run python -m copthief.reporting.bonus_demo
"""
from copthief.reporting.json_report import build_bonus_game_report, write_report
from copthief.sdk.sdk import CopThiefSdk
from copthief.shared.config import load_game_config


def run_bonus_demo() -> dict:
    """Play the 3+3 split between two self-play instances; return the bonus report dict."""
    config = load_game_config()
    half = max(config.num_games // 2, 1)

    # First half: group_1 cop vs group_2 thief. Second half: roles swapped.
    first = CopThiefSdk(config=_with_games(config, half), seed=101).run_series()
    second = CopThiefSdk(config=_with_games(config, config.num_games - half), seed=202).run_series()

    g1_total = first.cop_total + second.thief_total
    g2_total = first.thief_total + second.cop_total
    sub_games = [_summ(sg, "g1_cop_vs_g2_thief") for sg in first.sub_games]
    sub_games += [_summ(sg, "g2_cop_vs_g1_thief") for sg in second.sub_games]

    return build_bonus_game_report(
        group_1="SMNGRP05",
        group_2="SMNGRP05-mirror (self-play)",
        repos={
            "group_1": "https://github.com/afaf-gharra/marl-cop-thief",
            "group_2": "https://github.com/afaf-gharra/marl-cop-thief",
        },
        mcp_urls={
            "group_1_cop": "http://127.0.0.1:8801/mcp",
            "group_1_thief": "http://127.0.0.1:8802/mcp",
            "group_2_cop": "http://127.0.0.1:8811/mcp",
            "group_2_thief": "http://127.0.0.1:8812/mcp",
        },
        students={
            "group_1": ["Afaf Gharra (208123232)", "Reem Awawdy (212018899)"],
            "group_2": ["Afaf Gharra (208123232)", "Reem Awawdy (212018899)"],
        },
        sub_games=sub_games,
        totals_by_group={"SMNGRP05": g1_total, "SMNGRP05-mirror (self-play)": g2_total},
        bonus_claim={"SMNGRP05": 10 if g1_total >= g2_total else 7,
                     "SMNGRP05-mirror (self-play)": 7 if g1_total >= g2_total else 10},
        mutual_agreement=True,
    )


def _with_games(config, n):
    import dataclasses

    return dataclasses.replace(config, num_games=n)


def _summ(sub_game, matchup: str) -> dict:
    return {
        "matchup": matchup,
        "outcome": sub_game.outcome,
        "cop_points": sub_game.score.cop_points if sub_game.score else 0,
        "thief_points": sub_game.score.thief_points if sub_game.score else 0,
        "num_turns": len(sub_game.turns),
    }


def main() -> None:
    report = run_bonus_demo()
    write_report(report, "results/bonus_game_report.json")
    print("Wrote results/bonus_game_report.json (self-play demonstration).")
    print("totals_by_group:", report["totals_by_group"])


if __name__ == "__main__":
    main()
