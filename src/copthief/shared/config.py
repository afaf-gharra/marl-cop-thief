"""Configuration loader. All gameplay/rate-limit parameters come from JSON files — never hardcoded."""
import json
import os
from dataclasses import dataclass
from pathlib import Path

from copthief.shared.constants import DEFAULT_CONFIG_PATH, DEFAULT_RATE_LIMIT_PATH
from copthief.shared.version import assert_config_version_compatible


@dataclass(frozen=True)
class ScoringConfig:
    cop_win: int
    thief_win: int
    cop_loss: int
    thief_loss: int


@dataclass(frozen=True)
class GameConfig:
    version: str
    grid_size: tuple[int, int]
    max_moves: int
    num_games: int
    max_barriers: int
    scoring: ScoringConfig
    group_name: str
    timezone: str
    report_recipient: str


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "config").is_dir():
            return candidate
    return start


def load_game_config(path: str | None = None) -> GameConfig:
    """Load and validate config/config.json."""
    repo_root = _find_repo_root(Path(__file__))
    resolved = Path(path) if path else repo_root / DEFAULT_CONFIG_PATH
    with open(resolved, encoding="utf-8") as handle:
        raw = json.load(handle)

    assert_config_version_compatible(raw.get("version", ""))

    grid = raw["grid_size"]
    scoring = raw["scoring"]
    return GameConfig(
        version=raw["version"],
        grid_size=(grid[0], grid[1]),
        max_moves=raw["max_moves"],
        num_games=raw["num_games"],
        max_barriers=raw["max_barriers"],
        scoring=ScoringConfig(
            cop_win=scoring["cop_win"],
            thief_win=scoring["thief_win"],
            cop_loss=scoring["cop_loss"],
            thief_loss=scoring["thief_loss"],
        ),
        group_name=raw.get("group_name", "UNKNOWN"),
        timezone=raw.get("timezone", "UTC"),
        report_recipient=raw.get("report_recipient", ""),
    )


def load_rate_limits(path: str | None = None) -> dict:
    """Load config/rate_limits.json."""
    repo_root = _find_repo_root(Path(__file__))
    resolved = Path(path) if path else repo_root / DEFAULT_RATE_LIMIT_PATH
    with open(resolved, encoding="utf-8") as handle:
        return json.load(handle)


def get_env(key: str, default: str | None = None) -> str | None:
    """Read a secret/setting from the environment only — never from source code."""
    return os.environ.get(key, default)
