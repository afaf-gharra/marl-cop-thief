"""Shared pytest fixtures. No test in this suite depends on a live LLM or Google API."""
import pytest

from copthief.shared.config import GameConfig, QLearningConfig, ScoringConfig


@pytest.fixture(autouse=True)
def _no_real_api_keys(monkeypatch):
    """Strip LLM keys (auto-loaded from .env) so no test can ever hit a paid API.

    Tests that exercise provider selection set their own fake keys explicitly.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def scoring() -> ScoringConfig:
    return ScoringConfig(cop_win=20, thief_win=10, cop_loss=5, thief_loss=5)

@pytest.fixture
def small_config(scoring) -> GameConfig:
    return GameConfig(
        version="1.00",
        grid_size=(3, 3),
        max_moves=10,
        num_games=2,
        max_barriers=2,
        scoring=scoring,
        q_learning=QLearningConfig(learning_rate=0.1, discount_factor=0.9, epsilon=0.2),
        group_name="SMNGRP05",
        timezone="Asia/Jerusalem",
        report_recipient="rmisegal+uoh26b@gmail.com",
    )
