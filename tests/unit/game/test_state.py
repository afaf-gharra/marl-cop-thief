from copthief.game.grid import Grid
from copthief.game.state import GameState
from copthief.shared.constants import Role


def _state(cop=(0, 0), thief=(4, 4)):
    grid = Grid(rows=5, cols=5, max_barriers=5)
    return GameState(grid=grid, cop_pos=cop, thief_pos=thief)


def test_is_capture():
    assert not _state().is_capture()
    assert _state(cop=(2, 2), thief=(2, 2)).is_capture()


def test_manhattan_distance():
    assert _state(cop=(0, 0), thief=(0, 3)).manhattan_distance() == 3


def test_partial_view_hides_opponent_position():
    state = _state(cop=(0, 0), thief=(4, 4))
    view = state.partial_view(Role.COP)
    assert view["own_position"] == [0, 0]
    assert "thief" not in str(view).lower() or "position" not in view


def test_distance_bucket_thresholds():
    assert _state(cop=(0, 0), thief=(0, 0)).partial_view(Role.COP)["distance_hint"] == "adjacent"
    assert _state(cop=(0, 0), thief=(0, 3)).partial_view(Role.COP)["distance_hint"] == "close"
    assert _state(cop=(0, 0), thief=(4, 0)).partial_view(Role.COP)["distance_hint"] == "medium"
    assert _state(cop=(0, 0), thief=(0, 20)).partial_view(Role.COP)["distance_hint"] == "far"
