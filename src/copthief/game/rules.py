"""Move validation and win-condition checks for one sub-game."""
from copthief.game.state import GameState
from copthief.shared.constants import MOVE_DELTAS, Action, Outcome, Role


def legal_actions(state: GameState, role: Role) -> list[Action]:
    """Return the actions that are legal for `role` right now."""
    actions = [a for a in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT) if _can_move(state, role, a)]
    if role == Role.COP and state.barriers_placed_by_cop < state.grid.max_barriers:
        actions.append(Action.PLACE_BARRIER)
    return actions


def _target_cell(state: GameState, role: Role, action: Action) -> tuple[int, int]:
    pos = state.cop_pos if role == Role.COP else state.thief_pos
    dr, dc = MOVE_DELTAS[action]
    return pos[0] + dr, pos[1] + dc


def _can_move(state: GameState, role: Role, action: Action) -> bool:
    target = _target_cell(state, role, action)
    if not state.grid.in_bounds(target):
        return False
    return not state.grid.is_barrier(target)


def apply_action(state: GameState, role: Role, action: Action, barrier_target: tuple[int, int] | None = None) -> bool:
    """Apply a validated action to the state in place. Returns True if the action was legal and applied."""
    if action == Action.PLACE_BARRIER:
        if role != Role.COP or barrier_target is None:
            return False
        placed = state.grid.place_barrier(barrier_target, state.occupied_cells())
        if placed:
            state.barriers_placed_by_cop += 1
        return placed

    if not _can_move(state, role, action):
        return False
    target = _target_cell(state, role, action)
    if role == Role.COP:
        state.cop_pos = target
    else:
        state.thief_pos = target
    return True


def check_capture(state: GameState) -> Outcome | None:
    """Return COP_WINS if the cop has just captured the thief, else None.

    Survival (THIEF_WINS) is decided by the orchestrator once `max_moves` is
    reached without a capture — that boundary is a run parameter, not a rule.
    """
    return Outcome.COP_WINS if state.is_capture() else None
