# PRD — Natural-Language MCP Communication Protocol

## Theoretical background

Per the exercise spec (§3, §5), the two agents must communicate only
through free natural language relayed via **independent MCP servers** — no
shared memory, no direct function calls. Each server (`cop_server.py`,
`thief_server.py`, built from the shared `mcp_servers/factory.py`) exposes a
`take_turn` tool that receives the opponent's last message plus the agent's
own partial view, and must (1) interpret the message, (2) infer the
opponent's likely situation, and (3) translate that into one legal grid
action — the three steps required by the spec.

## Requirements: input/output, performance targets

- Input: `partial_view` (own position, grid size, visible barriers, turn
  count, coarse distance hint — never the opponent's exact cell),
  `incoming_message` (free text), `legal_actions` (list of action names).
- Output: `{"message": str, "action": str}` where `action` is one of the
  supplied `legal_actions`.
- Performance: one LLM call per turn, rate-limited to 20 requests/min via
  `ApiGatekeeper` (`config/rate_limits.json`, service `"llm"`).

## Constraints, trade-offs, rationale

- **Offline fallback is mandatory, not optional**: `nl_protocol.template_fallback`
  produces the same JSON-shaped output using only the Q-learning suggestion
  and string templates, so the MCP contract and the game loop are
  identical whether or not `ANTHROPIC_API_KEY` is set. This satisfies the
  submission guideline that no automated test may depend on an external
  service.
- **In-process vs. HTTP transport**: the default run (`copthief.main`) uses
  `fastmcp.Client` against the `FastMCP` server objects directly (in-memory
  transport) for speed and CI-friendliness; `cop_server.py`/`thief_server.py`
  remain independently runnable as HTTP services on `127.0.0.1:8801`/`8802`
  for a genuine two-process demonstration (see `docs/PLAN.md`).
- **Action legality is re-validated by the orchestrator**, never trusted
  blindly from the LLM/template reply — `nl_protocol.parse_reply` falls back
  to the Q-learning suggestion if the LLM names an illegal or malformed
  action.

## Success criteria and specific test scenarios

- `tests/unit/agents/test_nl_protocol.py`: `parse_reply` correctly extracts
  the `ACTION: <name>` tag and falls back safely on malformed/illegal
  actions; `template_fallback` never returns an action outside the legal
  set.
- `tests/integration/test_sanity_checks.py`: full sub-games at grid sizes
  2×2 through 5×5 complete without exceeding `max_moves`, using the offline
  fallback exclusively (Table 2's graduated sanity checks).
