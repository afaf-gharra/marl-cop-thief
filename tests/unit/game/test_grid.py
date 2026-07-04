import random

from copthief.game.grid import Grid


def test_in_bounds():
    grid = Grid(rows=5, cols=5, max_barriers=5)
    assert grid.in_bounds((0, 0))
    assert grid.in_bounds((4, 4))
    assert not grid.in_bounds((5, 0))
    assert not grid.in_bounds((-1, 0))


def test_place_barrier_respects_limit():
    grid = Grid(rows=5, cols=5, max_barriers=1)
    assert grid.place_barrier((1, 1), occupied=set())
    assert not grid.place_barrier((2, 2), occupied=set())
    assert grid.barriers == {(1, 1)}


def test_cannot_place_barrier_on_occupied_or_existing():
    grid = Grid(rows=5, cols=5, max_barriers=5)
    assert not grid.place_barrier((1, 1), occupied={(1, 1)})
    grid.place_barrier((2, 2), occupied=set())
    assert not grid.place_barrier((2, 2), occupied=set())


def test_random_free_cell_avoids_occupied_and_barriers():
    grid = Grid(rows=2, cols=2, max_barriers=5)
    grid.barriers.add((0, 1))
    rng = random.Random(0)
    cell = grid.random_free_cell(occupied={(0, 0)}, rng=rng)
    assert cell == (1, 1)
