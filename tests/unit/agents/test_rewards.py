from copthief.agents.rewards import step_reward
from copthief.shared.constants import Role


def test_cop_step_penalty_and_capture_reward():
    assert step_reward(Role.COP, captured=False) < 0
    assert step_reward(Role.COP, captured=True) > 0


def test_thief_survive_reward_and_caught_penalty():
    assert step_reward(Role.THIEF, captured=False) > 0
    assert step_reward(Role.THIEF, captured=True) < 0
