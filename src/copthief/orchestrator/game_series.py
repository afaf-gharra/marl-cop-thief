"""Runs a full series of `num_games` sub-games, retrying technical losses so a valid
series always completes (per the exercise's technical-loss handling rule)."""
import random
from dataclasses import dataclass, field

from fastmcp import Client

from copthief.orchestrator.sub_game import SubGameRecord, run_sub_game
from copthief.shared.config import GameConfig
from copthief.shared.constants import Outcome

_MAX_ATTEMPTS_MULTIPLIER = 3


@dataclass
class SeriesResult:
    sub_games: list[SubGameRecord] = field(default_factory=list)
    cop_total: int = 0
    thief_total: int = 0


async def run_game_series(
    cop_client: Client,
    thief_client: Client,
    config: GameConfig,
    rng: random.Random | None = None,
) -> SeriesResult:
    """Play `config.num_games` valid sub-games, replaying any that end in a technical loss."""
    rng = rng or random.Random()
    result = SeriesResult()
    attempts = 0
    max_attempts = config.num_games * _MAX_ATTEMPTS_MULTIPLIER

    while len(result.sub_games) < config.num_games and attempts < max_attempts:
        attempts += 1
        record = await run_sub_game(cop_client, thief_client, config, rng)
        if record.outcome == Outcome.TECHNICAL_LOSS.value:
            continue
        result.sub_games.append(record)
        result.cop_total += record.score.cop_points
        result.thief_total += record.score.thief_points

    return result
