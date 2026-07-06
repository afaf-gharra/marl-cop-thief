"""Graduated sanity checks (spec Table 2): algorithmic soundness across increasing grid sizes,
run fully offline (no ANTHROPIC_API_KEY) so these never depend on an external service."""
import random

import pytest
from fastmcp import Client

from copthief.mcp_servers.factory import build_agent_server
from copthief.orchestrator.game_series import run_game_series
from copthief.shared.config import GameConfig, QLearningConfig, ScoringConfig
from copthief.shared.constants import Outcome, Role


def _config(grid_size: tuple[int, int], max_moves: int, num_games: int = 2) -> GameConfig:
    return GameConfig(
        version="1.00",
        grid_size=grid_size,
        max_moves=max_moves,
        num_games=num_games,
        max_barriers=2,
        scoring=ScoringConfig(cop_win=20, thief_win=10, cop_loss=5, thief_loss=5),
        q_learning=QLearningConfig(learning_rate=0.1, discount_factor=0.9, epsilon=0.2),
        group_name="SMNGRP05",
        timezone="Asia/Jerusalem",
        report_recipient="",
    )


@pytest.mark.parametrize(
    "grid_size,max_moves",
    [
        ((2, 2), 6),
        ((3, 3), 12),
        ((4, 4), 20),
        ((5, 5), 25),
    ],
)
async def test_graduated_sanity_check(grid_size, max_moves, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = _config(grid_size, max_moves)
    cop_server = build_agent_server(Role.COP)
    thief_server = build_agent_server(Role.THIEF)

    async with Client(cop_server) as cop_client, Client(thief_server) as thief_client:
        result = await run_game_series(cop_client, thief_client, config, random.Random(42))

    assert len(result.sub_games) == config.num_games
    for sub_game in result.sub_games:
        assert sub_game.outcome in (Outcome.COP_WINS.value, Outcome.THIEF_WINS.value)
        assert len(sub_game.turns) <= config.max_moves
        assert sub_game.score is not None
