"""N x M grid with barrier placement, sized dynamically from config."""
from dataclasses import dataclass, field

Position = tuple[int, int]


@dataclass
class Grid:
    """A rectangular grid supporting barrier placement up to a configured maximum."""

    rows: int
    cols: int
    max_barriers: int
    barriers: set[Position] = field(default_factory=set)

    def in_bounds(self, pos: Position) -> bool:
        row, col = pos
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_barrier(self, pos: Position) -> bool:
        return pos in self.barriers

    def can_place_barrier(self, pos: Position, occupied: set[Position]) -> bool:
        return (
            len(self.barriers) < self.max_barriers
            and self.in_bounds(pos)
            and pos not in self.barriers
            and pos not in occupied
        )

    def place_barrier(self, pos: Position, occupied: set[Position]) -> bool:
        """Attempt to place a barrier; returns True on success, False if the move was illegal."""
        if not self.can_place_barrier(pos, occupied):
            return False
        self.barriers.add(pos)
        return True

    def random_free_cell(self, occupied: set[Position], rng) -> Position:
        """Pick a random cell not occupied by an agent or a barrier."""
        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in occupied and (r, c) not in self.barriers
        ]
        return rng.choice(candidates)
