"""Tabular Q-Learning move optimizer (Bellman update), per the exercise spec section 8."""
import random

import numpy as np

from copthief.shared.constants import Action


class QLearningAgent:
    """One Q-table per role. States are grid cells; actions are the role's legal move set."""

    def __init__(
        self,
        num_states: int,
        actions: list[Action],
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.2,
        rng: random.Random | None = None,
    ):
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = np.zeros((num_states, len(actions)))
        self._rng = rng or random.Random()

    def choose_action(self, state: int, legal_actions: list[Action]) -> Action:
        """Epsilon-greedy selection restricted to the currently legal actions."""
        if not legal_actions:
            raise ValueError("No legal actions available to choose from.")
        legal_indices = [self.actions.index(a) for a in legal_actions]
        if self._rng.random() < self.epsilon:
            return self.actions[self._rng.choice(legal_indices)]
        best_index = max(legal_indices, key=lambda i: self.q_table[state, i])
        return self.actions[best_index]

    def update(self, state: int, action: Action, reward: float, next_state: int, done: bool) -> None:
        """Bellman update: Q(s,a) += alpha * (r + gamma * max_a' Q(s',a') - Q(s,a))."""
        action_index = self.actions.index(action)
        best_next_q = 0.0 if done else np.max(self.q_table[next_state])
        td_target = reward + self.discount_factor * best_next_q
        td_error = td_target - self.q_table[state, action_index]
        self.q_table[state, action_index] += self.learning_rate * td_error


def state_index(position: tuple[int, int], cols: int) -> int:
    """Flatten a (row, col) grid position into a single Q-table state index."""
    row, col = position
    return row * cols + col
