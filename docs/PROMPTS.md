# Prompt Engineering Log

Per the submission guidelines §8.3, this documents both (a) the runtime prompts
the agents use during play and (b) the build-time prompt strategy that produced
this project with an AI coding assistant.

## A. Runtime agent prompt (the game's own LLM usage)

Each agent turn issues exactly one LLM call, built by
`src/copthief/agents/nl_protocol.py::build_prompt`. The prompt deliberately
enforces the three reasoning steps the exercise requires (§3): interpret the
opponent's message, infer their situation, translate to a legal action.

**Template (per role):**
```
{role flavor: "You are the Cop, hunting the Thief..." / "You are the Thief, evading..."}
Your position: {own cell}. Grid size: {n×m}.
Turn: {t}. Opponent distance hint: {adjacent|close|medium|far}.
Opponent's last message: "{free text}"
1. Interpret what the opponent's message implies about their plan.
2. Infer their likely position or direction from that message and the distance hint.
3. Choose ONE action from: [{legal actions}]. Our optimizer suggests '{q_action}'
   but you may override it if the message changes your assessment.
Reply with a short free-text message to the opponent, then a final line exactly
'ACTION: <action_name>'.
```

**Design decisions and iterations:**

1. **Partial observability is enforced in the prompt, not just the code.** The
   prompt never contains the opponent's exact cell — only a coarse
   `distance_hint` bucket. This keeps the LLM honest to the Dec-POMDP model:
   it must *reason* about the opponent from language, not read their position.

2. **Q-table suggestion is offered, not imposed.** Early designs let the LLM
   pick freely, which produced legal-but-erratic play. Passing the Q-learning
   suggestion as advice — "you may override it" — grounds the LLM in the
   learned optimizer while preserving genuine free-language agency. Observed in
   `assets/llm_run_log.txt`: the cop frequently *does* override ("I will not go
   'up' as the optimizer suggests, since their last message implies...").

3. **Structured action tag with a safety net.** Requiring a final
   `ACTION: <name>` line makes parsing deterministic (`parse_reply`), and any
   missing/illegal action falls back to the Q-suggestion — so a chatty or
   malformed LLM reply can never crash a game or make an illegal move.

4. **Tight token budget.** `max_tokens=200` per call keeps a full 6-game series
   under one cent on `gpt-4o-mini` (see cost analysis in
   `notebooks/results_analysis.ipynb`) while leaving room for the visible
   free-text taunt the opponent then reads.

## B. Build-time prompt strategy (how this repo was produced)

The project was built with an AI coding assistant under a strict
"docs-and-architecture-before-code" workflow (guidelines §1.4). The prompt
sequence that worked:

1. **Ground the model in the two source PDFs first** — the exercise spec and
   the professional-software guidelines — and have it extract a combined
   requirements list before writing any code. This prevented the common
   failure of code that "works but ignores the rubric."

2. **Force an explicit plan artifact** (PRD/PLAN/TODO) and get approval before
   implementation, matching the guidelines' mandatory work process.

3. **Constrain every module to one concern and ≤150 lines up front**, so the
   assistant split files proactively (e.g. `llm_client.py` provider methods,
   `factory.py` shared server builder) instead of producing 400-line modules
   that later need surgery.

4. **Demand tests alongside each module (TDD-style)** and an offline fallback
   for every external dependency, so the whole suite runs with no network and
   no API keys — the single most valuable constraint for reproducible grading.

5. **Iterate against the real gates** (`ruff check`, `pytest --cov`) rather than
   eyeballing — each lint/coverage failure was fed straight back as the next
   prompt, converging quickly to zero violations and >90% coverage.

**Techniques that were tried and dropped:** letting the LLM manage game state
directly (rejected — violated the Server/Client separation and partial
observability); a single monolithic `Agent` subclass hierarchy per role
(rejected — duplicated the decision logic, violating the anti-duplication rule;
replaced by one `Role`-parameterized `Agent`).
