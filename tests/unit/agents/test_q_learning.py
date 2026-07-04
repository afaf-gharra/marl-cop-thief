import random

from copthief.agents.q_learning import QLearningAgent, state_index
from copthief.shared.constants import Action

_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]


def test_state_index_flattens_row_major():
    assert state_index((0, 0), cols=5) == 0
    assert state_index((1, 2), cols=5) == 7


def test_choose_action_restricted_to_legal_set():
    agent = QLearningAgent(num_states=9, actions=_ACTIONS, epsilon=1.0, rng=random.Random(0))
    for _ in range(20):
        action = agent.choose_action(0, legal_actions=[Action.UP, Action.DOWN])
        assert action in (Action.UP, Action.DOWN)


def test_update_increases_q_value_toward_reward():
    agent = QLearningAgent(num_states=9, actions=_ACTIONS, learning_rate=0.5, discount_factor=0.9)
    before = agent.q_table[0, 0]
    agent.update(state=0, action=Action.UP, reward=1.0, next_state=1, done=True)
    after = agent.q_table[0, 0]
    assert after > before


def test_terminal_update_does_not_bootstrap_next_state():
    agent = QLearningAgent(num_states=9, actions=_ACTIONS, learning_rate=1.0, discount_factor=0.9)
    agent.q_table[1, :] = 100.0
    agent.update(state=0, action=Action.UP, reward=1.0, next_state=1, done=True)
    assert agent.q_table[0, 0] == 1.0


def test_epsilon_zero_is_greedy():
    agent = QLearningAgent(num_states=9, actions=_ACTIONS, epsilon=0.0)
    agent.q_table[0, _ACTIONS.index(Action.DOWN)] = 5.0
    action = agent.choose_action(0, legal_actions=_ACTIONS)
    assert action == Action.DOWN
