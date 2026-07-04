"""Mutable state of a single sub-game episode and the partial-observability view builder."""
from dataclasses import dataclass

from copthief.game.grid import Grid, Position
from copthief.shared.constants import Role


@dataclass
class GameState:
    """Full (God's-eye) state of one sub-game. Agents never see this directly."""

    grid: Grid
    cop_pos: Position
    thief_pos: Position
    turn_count: int = 0
    barriers_placed_by_cop: int = 0
    current_turn: Role = Role.THIEF

    def occupied_cells(self) -> set[Position]:
        return {self.cop_pos, self.thief_pos}

    def is_capture(self) -> bool:
        return self.cop_pos == self.thief_pos

    def manhattan_distance(self) -> int:
        return abs(self.cop_pos[0] - self.thief_pos[0]) + abs(self.cop_pos[1] - self.thief_pos[1])

    def partial_view(self, role: Role) -> dict:
        """Build the partial observation an agent is allowed to see: own position,
        visible barriers, and turn/move counters — never the opponent's exact cell."""
        own_pos = self.cop_pos if role == Role.COP else self.thief_pos
        return {
            "role": role.value,
            "own_position": list(own_pos),
            "grid_size": [self.grid.rows, self.grid.cols],
            "barriers": [list(b) for b in sorted(self.grid.barriers)],
            "turn_count": self.turn_count,
            "barriers_remaining": self.grid.max_barriers - self.barriers_placed_by_cop,
            "distance_hint": self._distance_bucket(),
        }

    def _distance_bucket(self) -> str:
        """A coarse, qualitative hint only (not the exact opponent location)."""
        distance = self.manhattan_distance()
        if distance <= 1:
            return "adjacent"
        if distance <= 3:
            return "close"
        if distance <= self.grid.rows:
            return "medium"
        return "far"
