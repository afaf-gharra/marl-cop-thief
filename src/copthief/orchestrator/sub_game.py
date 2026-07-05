"""Drives a single sub-game (<=25 moves) by alternating MCP tool calls between the two agents."""
import random
from dataclasses import dataclass, field

from fastmcp import Client

from copthief.game import rules
from copthief.game.grid import Grid
from copthief.game.scoring import SubGameScore, score_sub_game
from copthief.game.state import GameState
from copthief.shared.config import GameConfig
from copthief.shared.constants import Action, Outcome, Role


@dataclass
class TurnRecord:
    role: str
    message: str
    action: str
    position_after: list[int]
    barrier_placed: list[int] | None = None


@dataclass
class SubGameRecord:
    outcome: str
    turns: list[TurnRecord] = field(default_factory=list)
    score: SubGameScore | None = None


def _initial_positions(grid: Grid, rng: random.Random) -> tuple[tuple[int, int], tuple[int, int]]:
    cop_pos = grid.random_free_cell(set(), rng)
    thief_pos = grid.random_free_cell({cop_pos}, rng)
    return cop_pos, thief_pos


def _pick_barrier_target(state: GameState, rng: random.Random) -> tuple[int, int] | None:
    row, col = state.cop_pos
    candidates = [
        (row + dr, col + dc)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
        if state.grid.can_place_barrier((row + dr, col + dc), state.occupied_cells())
    ]
    return rng.choice(candidates) if candidates else None


async def _take_turn(client: Client, role: Role, state: GameState, incoming_message: str) -> tuple[str, Action]:
    partial_view = state.partial_view(role)
    legal = rules.legal_actions(state, role)
    result = await client.call_tool(
        "take_turn",
        {
            "partial_view": partial_view,
            "incoming_message": incoming_message,
            "legal_actions": [a.value for a in legal],
        },
    )
    data = result.data if hasattr(result, "data") else result
    return data["message"], Action(data["action"])


async def run_sub_game(
    cop_client: Client,
    thief_client: Client,
    config: GameConfig,
    rng: random.Random | None = None,
) -> SubGameRecord:
    """Run one full sub-game episode and return its transcript, outcome, and score."""
    rng = rng or random.Random()
    grid = Grid(rows=config.grid_size[0], cols=config.grid_size[1], max_barriers=config.max_barriers)
    cop_pos, thief_pos = _initial_positions(grid, rng)
    state = GameState(grid=grid, cop_pos=cop_pos, thief_pos=thief_pos, current_turn=Role.THIEF)

    record = SubGameRecord(outcome="")
    last_message = ""

    try:
        while state.turn_count < config.max_moves:
            role = state.current_turn
            client = thief_client if role == Role.THIEF else cop_client

            message, action = await _take_turn(client, role, state, last_message)
            barrier_target = _pick_barrier_target(state, rng) if action == Action.PLACE_BARRIER else None
            applied = rules.apply_action(state, role, action, barrier_target)
            barrier_placed = list(barrier_target) if (applied and barrier_target is not None) else None

            position = state.thief_pos if role == Role.THIEF else state.cop_pos
            record.turns.append(
                TurnRecord(
                    role=role.value,
                    message=message,
                    action=action.value,
                    position_after=list(position),
                    barrier_placed=barrier_placed,
                )
            )
            last_message = message
            state.turn_count += 1
            state.current_turn = Role.COP if role == Role.THIEF else Role.THIEF

            if rules.check_capture(state) == Outcome.COP_WINS:
                record.outcome = Outcome.COP_WINS.value
                break
        else:
            record.outcome = Outcome.THIEF_WINS.value
    except Exception:  # noqa: BLE001 - any MCP/agent failure becomes a technical loss, not a crash
        record.outcome = Outcome.TECHNICAL_LOSS.value
        return record

    record.score = score_sub_game(Outcome(record.outcome), config.scoring)
    return record
