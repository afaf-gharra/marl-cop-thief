import random

from copthief.research.harness import new_agents, run_series


def test_run_series_returns_expected_keys(small_config):
    cop, thief = new_agents(small_config)
    result = run_series(cop, thief, small_config, random.Random(0))
    assert set(result) == {"cop_total", "thief_total", "cop_win_rate", "mean_turns"}
    assert 0.0 <= result["cop_win_rate"] <= 1.0
    assert result["mean_turns"] <= small_config.max_moves


def test_scores_are_consistent_with_win_rate(small_config):
    cop, thief = new_agents(small_config)
    result = run_series(cop, thief, small_config, random.Random(3))
    # cop_total is bounded by num_games * max possible per game
    assert result["cop_total"] >= small_config.num_games * min(
        small_config.scoring.cop_win, small_config.scoring.cop_loss
    )


def test_new_agents_have_independent_zeroed_qtables(small_config):
    cop, thief = new_agents(small_config)
    assert cop is not thief
    assert (cop._q_agent.q_table == 0).all()
    assert (thief._q_agent.q_table == 0).all()


def test_qtables_actually_update_during_play(small_config):
    """The Q-learning must genuinely learn during gameplay, not stay at zero."""
    import random

    cop, thief = new_agents(small_config)
    for _ in range(5):
        run_series(cop, thief, small_config, random.Random(0))
    # After several series, at least one agent's Q-table must have moved off zero.
    assert (cop._q_agent.q_table != 0).any() or (thief._q_agent.q_table != 0).any()
