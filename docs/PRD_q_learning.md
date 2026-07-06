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

## Reward feedback loop (learning during real games)

Learning is wired into actual gameplay, not just unit tests. After each turn
the orchestrator calls the agent's `report_outcome` MCP tool (in-process via
`copthief.research.harness` for parameter studies; over MCP via
`orchestrator/sub_game.py::_report_outcome` for real games) with a shaped
per-step reward from `copthief.agents.rewards`:

- Cop: `-1` per step (pushes for a fast capture), `+20` on capture.
- Thief: `+1` per surviving step, `-20` when caught.

Because both agents update their tables each turn, the tables genuinely
populate over a run (verified in the notebook: most of the 25×5 entries become
non-zero) and the two agents co-adapt.

## Success criteria and specific test scenarios

- `tests/unit/agents/test_q_learning.py` verifies: Q-values increase toward
  the rewarded action after repeated updates on a fixed state; the agent
  never selects an action outside the provided legal-action list; and a
  terminal (`done=True`) update does not bootstrap from the next state.
- `tests/unit/agents/test_rewards.py` verifies the reward signs per role.
- `tests/unit/research/test_harness.py::test_qtables_actually_update_during_play`
  proves the Q-tables move off zero during real gameplay (regression guard
  against the learning loop silently not firing).
