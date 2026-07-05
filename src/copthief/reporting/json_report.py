"""Builds the internal_game_report JSON exactly per the exercise spec (section 9.1)."""
import json
from pathlib import Path

from copthief.orchestrator.game_series import SeriesResult
from copthief.shared.config import GameConfig


def build_internal_game_report(
    result: SeriesResult,
    config: GameConfig,
    github_repo: str,
    cop_mcp_url: str,
    thief_mcp_url: str,
    students: list[str],
) -> dict:
    """Assemble the report dict matching the spec's internal_game_report schema."""
    return {
        "group_name": config.group_name,
        "students": students,
        "github_repo": github_repo,
        "cop_mcp_url": cop_mcp_url,
        "thief_mcp_url": thief_mcp_url,
        "timezone": config.timezone,
        "sub_games": [
            {
                "outcome": sub_game.outcome,
                "cop_points": sub_game.score.cop_points if sub_game.score else 0,
                "thief_points": sub_game.score.thief_points if sub_game.score else 0,
                "num_turns": len(sub_game.turns),
                "transcript": [
                    {
                        "role": turn.role,
                        "message": turn.message,
                        "action": turn.action,
                        "position_after": turn.position_after,
                        "barrier_placed": turn.barrier_placed,
                    }
                    for turn in sub_game.turns
                ],
            }
            for sub_game in result.sub_games
        ],
        "totals": {
            "cop": result.cop_total,
            "thief": result.thief_total,
        },
    }


def write_report(report: dict, path: str) -> None:
    """Persist the report as pretty-printed JSON, creating parent directories if needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
