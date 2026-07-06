"""Fast in-process research harness for parameter studies (guidelines §9).

Reuses the exact game rules (`game/rules.py`), state/partial-view, scoring, and
the `Agent` decision logic, but skips the MCP client/server transport so
hundreds of series run in seconds. The MCP transport itself is validated
separately (see tests/unit/mcp_servers/test_auth.py and the cloud deployment).
"""
import random

from copthief.agents.base_agent import Agent
from copthief.agents.q_learning import QLearningAgent
from copthief.agents.rewards import step_reward
from copthief.game import rules
from copthief.game.grid import Grid
from copthief.game.scoring import score_sub_game
from copthief.game.state import GameState
from copthief.shared.config import GameConfig
from copthief.shared.constants import Action, Outcome, Role

_COP_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.PLACE_BARRIER]
_THIEF_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]


def _make_agent(role: Role, config: GameConfig) -> Agent:
    actions = _COP_ACTIONS if role == Role.COP else _THIEF_ACTIONS
    q_agent = QLearningAgent(
        num_states=config.grid_size[0] * config.grid_size[1],
        actions=actions,
        learning_rate=config.q_learning.learning_rate,
        discount_factor=config.q_learning.discount_factor,
        epsilon=config.q_learning.epsilon,
    )
    return Agent(role=role, q_agent=q_agent, llm_client=None)


def _play_sub_game(cop: Agent, thief: Agent, config: GameConfig, rng: random.Random) -> tuple[str, int]:
    grid = Grid(rows=config.grid_size[0], cols=config.grid_size[1], max_barriers=config.max_barriers)
    cop_pos = grid.random_free_cell(set(), rng)
    thief_pos = grid.random_free_cell({cop_pos}, rng)
    state = GameState(grid=grid, cop_pos=cop_pos, thief_pos=thief_pos, current_turn=Role.THIEF)
    last_message = ""

    while state.turn_count < config.max_moves:
        role = state.current_turn
        agent = thief if role == Role.THIEF else cop
        legal = rules.legal_actions(state, role)
        if not legal:  # fully boxed in — the player passes (stays put) this turn
            state.turn_count += 1
            state.current_turn = Role.COP if role == Role.THIEF else Role.THIEF
            continue
        _, action = agent.decide(state.partial_view(role), last_message, legal)
        barrier = _pick_barrier(state, rng) if action == Action.PLACE_BARRIER else None
        rules.apply_action(state, role, action, barrier)
        last_message = f"{role.value} moved {action.value}"
        state.turn_count += 1
        state.current_turn = Role.COP if role == Role.THIEF else Role.THIEF

        captured = rules.check_capture(state) == Outcome.COP_WINS
        agent.learn(step_reward(role, captured), state.partial_view(role), done=captured)
        if captured:
            return Outcome.COP_WINS.value, state.turn_count
    return Outcome.THIEF_WINS.value, state.turn_count


def _pick_barrier(state: GameState, rng: random.Random):
    row, col = state.cop_pos
    options = [
        (row + dr, col + dc)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
        if state.grid.can_place_barrier((row + dr, col + dc), state.occupied_cells())
    ]
    return rng.choice(options) if options else None


def run_series(cop: Agent, thief: Agent, config: GameConfig, rng: random.Random) -> dict:
    """Play one series of `num_games` sub-games; return outcome counts and score totals."""
    cop_total = thief_total = cop_wins = turns = 0
    for _ in range(config.num_games):
        outcome, n_turns = _play_sub_game(cop, thief, config, rng)
        score = score_sub_game(Outcome(outcome), config.scoring)
        cop_total += score.cop_points
        thief_total += score.thief_points
        cop_wins += outcome == Outcome.COP_WINS.value
        turns += n_turns
    return {
        "cop_total": cop_total,
        "thief_total": thief_total,
        "cop_win_rate": cop_wins / config.num_games,
        "mean_turns": turns / config.num_games,
    }


def new_agents(config: GameConfig) -> tuple[Agent, Agent]:
    """Fresh cop/thief agents with zeroed Q-tables (for independent experiments)."""
    return _make_agent(Role.COP, config), _make_agent(Role.THIEF, config)
