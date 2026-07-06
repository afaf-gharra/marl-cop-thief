"""Shared builder for the Cop and Thief MCP servers (identical wiring, different role/port —
kept in one place instead of duplicated across the two server files)."""
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from copthief.agents.base_agent import Agent
from copthief.agents.llm_client import LlmClient
from copthief.agents.q_learning import QLearningAgent
from copthief.shared.config import GameConfig, get_env, load_game_config, load_rate_limits
from copthief.shared.constants import Action, Role
from copthief.shared.gatekeeper import ApiGatekeeper

_COP_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.PLACE_BARRIER]
_THIEF_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]


def _auth_provider() -> StaticTokenVerifier | None:
    """Require a Bearer token when MCP_AUTH_TOKEN is set (mandatory for cloud exposure)."""
    token = get_env("MCP_AUTH_TOKEN")
    if not token:
        return None
    return StaticTokenVerifier(tokens={token: {"client_id": "copthief-orchestrator"}})


def build_agent_server(role: Role, config: GameConfig | None = None) -> FastMCP:
    """Construct an independent FastMCP server exposing one tool: take_turn."""
    config = config or load_game_config()
    rate_limits = load_rate_limits()
    num_states = config.grid_size[0] * config.grid_size[1]
    actions = _COP_ACTIONS if role == Role.COP else _THIEF_ACTIONS

    gatekeeper = ApiGatekeeper(rate_limits, service="llm")
    llm_client = LlmClient(gatekeeper)
    q_agent = QLearningAgent(
        num_states=num_states,
        actions=actions,
        learning_rate=config.q_learning.learning_rate,
        discount_factor=config.q_learning.discount_factor,
        epsilon=config.q_learning.epsilon,
    )
    agent = Agent(role=role, q_agent=q_agent, llm_client=llm_client)

    mcp = FastMCP(name=f"copthief-{role.value}", auth=_auth_provider())

    @mcp.tool()
    def take_turn(partial_view: dict, incoming_message: str, legal_actions: list[str]) -> dict:
        """Decode the opponent's message, infer their situation, and choose one legal action.

        Args:
            partial_view: this agent's partial observation of the board.
            incoming_message: the opponent's last free-text message (empty on turn 1).
            legal_actions: the action names currently legal for this agent.
        """
        actions = [Action(a) for a in legal_actions]
        message, action = agent.decide(partial_view, incoming_message, actions)
        return {"message": message, "action": action.value}

    @mcp.tool()
    def report_outcome(reward: float, next_partial_view: dict, done: bool) -> dict:
        """Feed the result of the last turn back into this agent's Q-table."""
        agent.learn(reward, next_partial_view, done)
        return {"acknowledged": True}

    return mcp
