"""Single Agent implementation shared by both roles (parameterized, not subclassed, to
avoid the duplicate-logic-across-classes pattern the submission guidelines forbid)."""
import random

from copthief.agents.llm_client import LlmClient, NoApiKeyError
from copthief.agents.nl_protocol import build_prompt, parse_reply, template_fallback
from copthief.agents.q_learning import QLearningAgent, state_index
from copthief.shared.constants import Action, Role


class Agent:
    """Decides one turn: interpret incoming text, pick a move via Q-learning, phrase a reply."""

    def __init__(
        self,
        role: Role,
        q_agent: QLearningAgent,
        llm_client: LlmClient | None = None,
        rng: random.Random | None = None,
    ):
        self.role = role
        self._q_agent = q_agent
        self._llm_client = llm_client
        self._rng = rng or random.Random()
        self._last_state_index: int | None = None
        self._last_action: Action | None = None

    def decide(self, partial_view: dict, incoming_message: str, legal_actions: list[Action]) -> tuple[str, Action]:
        """Template method: Q-learning proposes an action, the NL layer phrases/confirms it."""
        cols = partial_view["grid_size"][1]
        state = state_index(tuple(partial_view["own_position"]), cols)
        suggested = self._q_agent.choose_action(state, legal_actions)

        message, action = self._generate_reply(partial_view, incoming_message, legal_actions, suggested)

        self._last_state_index = state
        self._last_action = action
        return message, action

    def _generate_reply(
        self,
        partial_view: dict,
        incoming_message: str,
        legal_actions: list[Action],
        suggested: Action,
    ) -> tuple[str, Action]:
        if self._llm_client is not None:
            try:
                prompt = build_prompt(self.role, partial_view, incoming_message, legal_actions, suggested)
                raw_reply = self._llm_client.complete(prompt)
                return parse_reply(raw_reply, legal_actions, fallback=suggested)
            except NoApiKeyError:
                pass
        return template_fallback(self.role, partial_view, suggested, self._rng)

    def learn(self, reward: float, next_partial_view: dict, done: bool) -> None:
        """Feed back the outcome of the last decision into the Q-table."""
        if self._last_state_index is None or self._last_action is None:
            return
        cols = next_partial_view["grid_size"][1]
        next_state = state_index(tuple(next_partial_view["own_position"]), cols)
        self._q_agent.update(self._last_state_index, self._last_action, reward, next_state, done)
