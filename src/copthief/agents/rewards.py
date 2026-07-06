"""Per-step reward shaping for the Q-learning agents (the `r` in the Bellman update).

The cop is pushed to capture quickly (small step penalty, large capture bonus);
the thief is rewarded for surviving each step and penalised for being caught.
These are learning signals only — they do not affect the official scoring table.
"""
from copthief.shared.constants import Role

STEP_PENALTY_COP = -1.0
CAPTURE_REWARD_COP = 20.0
SURVIVE_REWARD_THIEF = 1.0
CAUGHT_PENALTY_THIEF = -20.0


def step_reward(role: Role, captured: bool) -> float:
    """Reward for `role` after a turn, given whether the cop has just captured the thief."""
    if role == Role.COP:
        return CAPTURE_REWARD_COP if captured else STEP_PENALTY_COP
    return CAUGHT_PENALTY_THIEF if captured else SURVIVE_REWARD_THIEF
