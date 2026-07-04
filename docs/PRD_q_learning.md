# PRD — Tabular Q-Learning Move Optimizer

## Theoretical background

Each agent maintains a Q-table `Q(s, a)` over its own grid-cell states and
its legal action set (4 movement actions for the thief; 4 + place_barrier
for the cop). Updates follow the standard Bellman equation:

```
Q(s, a) <- Q(s, a) + alpha * [ r + gamma * max_a' Q(s', a') - Q(s, a) ]
```

implemented in `src/copthief/agents/q_learning.py::QLearningAgent.update`.
Action selection is epsilon-greedy (`choose_action`), restricted to the
actions currently legal under `game/rules.py::legal_actions` so the table
never proposes an illegal move.

## Requirements: input/output, performance targets

- Input: flattened `(row, col)` state index (`state_index`), a legal action
  list, and a scalar reward.
- Output: one `Action` per turn; the Q-table is updated once per turn via
  `Agent.learn(...)`.
- Performance: table size is `grid_rows * grid_cols` states — for the
  default 5×5 grid this is 25 states, well within the O(1) lookup budget
  needed for a 25-move sub-game.

## Constraints, trade-offs, rationale

- **State representation is intentionally coarse** (own position only, no
  opponent position) to respect the exercise's partial-observability
  requirement — the agent cannot condition its Q-values on information it
  isn't allowed to see. The opponent's influence instead reaches the agent
  through the natural-language message, handled by `nl_protocol.py`.
- Chose tabular Q-learning over a neural policy per the exercise's own
  recommendation (§8): no training infrastructure needed, and the resulting
  table is small enough to reset/reinitialize per test run.

## Success criteria and specific test scenarios

- `tests/unit/agents/test_q_learning.py` verifies: Q-values increase toward
  the rewarded action after repeated updates on a fixed state; the agent
  never selects an action outside the provided legal-action list; and a
  terminal (`done=True`) update does not bootstrap from the next state.
