import random

from copthief.agents.base_agent import Agent
from copthief.agents.q_learning import QLearningAgent
from copthief.shared.constants import Action, Role

_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

_VIEW = {
    "role": "thief",
    "own_position": [0, 0],
    "grid_size": [3, 3],
    "barriers": [],
    "turn_count": 0,
    "barriers_remaining": 0,
    "distance_hint": "far",
}


def test_decide_without_llm_client_uses_template_fallback():
    agent = Agent(Role.THIEF, QLearningAgent(9, _ACTIONS, epsilon=0.0), llm_client=None, rng=random.Random(0))
    message, action = agent.decide(_VIEW, "", legal_actions=[Action.DOWN])
    assert action == Action.DOWN
    assert isinstance(message, str) and message


class _RaisingLlmClient:
    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        from copthief.agents.llm_client import NoApiKeyError

        raise NoApiKeyError("no key")


def test_decide_falls_back_when_llm_raises_no_api_key():
    agent = Agent(
        Role.THIEF,
        QLearningAgent(9, _ACTIONS, epsilon=0.0),
        llm_client=_RaisingLlmClient(),
        rng=random.Random(0),
    )
    message, action = agent.decide(_VIEW, "", legal_actions=[Action.LEFT])
    assert action == Action.LEFT


def test_learn_updates_q_table_after_decide():
    q_agent = QLearningAgent(9, _ACTIONS, learning_rate=0.5, epsilon=0.0)
    agent = Agent(Role.THIEF, q_agent, llm_client=None, rng=random.Random(0))
    agent.decide(_VIEW, "", legal_actions=[Action.DOWN])
    before = q_agent.q_table.copy()
    agent.learn(reward=1.0, next_partial_view=_VIEW, done=True)
    assert not (q_agent.q_table == before).all()


def test_learn_without_prior_decide_is_a_no_op():
    q_agent = QLearningAgent(9, _ACTIONS)
    agent = Agent(Role.THIEF, q_agent, llm_client=None)
    agent.learn(reward=1.0, next_partial_view=_VIEW, done=True)
    assert (q_agent.q_table == 0).all()
