"""Scoring for a single sub-game, driven entirely by config (no hardcoded point values)."""
from dataclasses import dataclass

from copthief.shared.config import ScoringConfig
from copthief.shared.constants import Outcome


@dataclass(frozen=True)
class SubGameScore:
    cop_points: int
    thief_points: int


def score_sub_game(outcome: Outcome, scoring: ScoringConfig) -> SubGameScore:
    """Translate a sub-game outcome into cop/thief points per the configured scoring table."""
    if outcome == Outcome.COP_WINS:
        return SubGameScore(cop_points=scoring.cop_win, thief_points=scoring.thief_loss)
    if outcome == Outcome.THIEF_WINS:
        return SubGameScore(cop_points=scoring.cop_loss, thief_points=scoring.thief_win)
    raise ValueError(f"Cannot score outcome: {outcome}")
