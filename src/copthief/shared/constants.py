"""Immutable project-wide constants (no gameplay tuning values — those live in config/)."""
from enum import StrEnum


class Role(StrEnum):
    COP = "cop"
    THIEF = "thief"


class Action(StrEnum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PLACE_BARRIER = "place_barrier"


class Outcome(StrEnum):
    COP_WINS = "cop_wins"
    THIEF_WINS = "thief_wins"
    TECHNICAL_LOSS = "technical_loss"


MOVE_DELTAS: dict[Action, tuple[int, int]] = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}

DEFAULT_CONFIG_PATH = "config/config.json"
DEFAULT_RATE_LIMIT_PATH = "config/rate_limits.json"
COP_MCP_PORT = 8801
THIEF_MCP_PORT = 8802
