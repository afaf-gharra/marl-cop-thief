import pytest

from copthief.game.scoring import score_sub_game
from copthief.shared.constants import Outcome


def test_cop_wins_scoring(scoring):
    score = score_sub_game(Outcome.COP_WINS, scoring)
    assert score.cop_points == 20
    assert score.thief_points == 5


def test_thief_wins_scoring(scoring):
    score = score_sub_game(Outcome.THIEF_WINS, scoring)
    assert score.cop_points == 5
    assert score.thief_points == 10


def test_technical_loss_raises(scoring):
    with pytest.raises(ValueError):
        score_sub_game(Outcome.TECHNICAL_LOSS, scoring)
