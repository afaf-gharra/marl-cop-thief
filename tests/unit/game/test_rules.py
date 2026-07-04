from copthief.game import rules
from copthief.game.grid import Grid
from copthief.game.state import GameState
from copthief.shared.constants import Action, Outcome, Role


def _state():
    grid = Grid(rows=3, cols=3, max_barriers=2)
    return GameState(grid=grid, cop_pos=(1, 1), thief_pos=(0, 0))


def test_legal_actions_excludes_out_of_bounds():
    state = GameState(grid=Grid(rows=3, cols=3, max_barriers=2), cop_pos=(0, 0), thief_pos=(2, 2))
    legal = rules.legal_actions(state, Role.COP)
    assert Action.UP not in legal
    assert Action.LEFT not in legal
    assert Action.PLACE_BARRIER in legal


def test_legal_actions_excludes_barrier_cells():
    state = _state()
    state.grid.barriers.add((0, 1))
    legal = rules.legal_actions(state, Role.THIEF)
    assert Action.RIGHT not in legal


def test_thief_never_gets_place_barrier():
    state = _state()
    assert Action.PLACE_BARRIER not in rules.legal_actions(state, Role.THIEF)


def test_apply_move_updates_position():
    state = _state()
    assert rules.apply_action(state, Role.COP, Action.UP)
    assert state.cop_pos == (0, 1)


def test_apply_illegal_move_rejected():
    state = GameState(grid=Grid(rows=3, cols=3, max_barriers=2), cop_pos=(0, 0), thief_pos=(2, 2))
    assert not rules.apply_action(state, Role.COP, Action.UP)
    assert state.cop_pos == (0, 0)


def test_apply_barrier_increments_counter():
    state = _state()
    assert rules.apply_action(state, Role.COP, Action.PLACE_BARRIER, barrier_target=(2, 2))
    assert state.barriers_placed_by_cop == 1
    assert (2, 2) in state.grid.barriers


def test_apply_barrier_without_target_or_wrong_role_fails():
    state = _state()
    assert not rules.apply_action(state, Role.COP, Action.PLACE_BARRIER, barrier_target=None)
    assert not rules.apply_action(state, Role.THIEF, Action.PLACE_BARRIER, barrier_target=(2, 2))


def test_check_capture():
    state = _state()
    assert rules.check_capture(state) is None
    state.cop_pos = state.thief_pos
    assert rules.check_capture(state) == Outcome.COP_WINS
