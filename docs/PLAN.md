# Architecture & Planning

## C4-style overview

- **Context**: A student runs the CLI locally; two AI agents (Cop, Thief)
  play a pursuit game; a JSON report is optionally emailed to the course
  address.
- **Containers**: `copthief` Python package — `sdk` (facade), `orchestrator`
  (game-series driver), two `mcp_servers` (FastMCP instances), `agents`
  (decision layer), `game` (rules engine), `reporting`, `gui`.
- **Components**: see the tree in the plan file
  `~/.claude/plans/ex06-dual-ai-agent-race-linked-lollipop.md` — reproduced
  here:

```
sdk/sdk.py            -> CopThiefSdk facade, single external entry point
orchestrator/          -> sub_game.py (one episode), game_series.py (6 episodes + retry)
mcp_servers/           -> factory.py (shared builder), cop_server.py, thief_server.py
agents/                -> base_agent.py (Template Method), q_learning.py, nl_protocol.py, llm_client.py
game/                  -> grid.py, state.py, rules.py, scoring.py
reporting/             -> json_report.py, gmail_sender.py
gui/                   -> console_view.py (ASCII + matplotlib)
shared/                -> config.py, constants.py, gatekeeper.py, version.py
```

- **Code**: each module ≤150 lines; one class/concept per file.

## Deployment stages (staged rollout per exercise §6)

1. **Local (default, tested)**: `CopThiefSdk` builds both `FastMCP` server
   instances and drives them via an in-process `fastmcp.Client` — this still
   goes through the full MCP tool-call protocol (JSON schemas, tool
   dispatch), just without opening a TCP socket, so it is fast and
   deterministic for CI/grading.
2. **Local, two processes (documented, user-run)**: `cop_server.py` and
   `thief_server.py` each `app.run(transport="http", port=8801/8802)` — run
   in two terminals for a genuine two-process, two-port demonstration.
3. **Cloud (documented, not executed)**: push the same FastMCP apps behind
   Prefect Cloud or an `ngrok`/`Localtonet` tunnel with `Authorization`
   header auth, per the exercise's Access-1 (simple cloud API) recommendation
   for the LLM call and Access-3 (hybrid) recommendation for the MCP
   servers. Requires the student's own cloud/tunnel accounts.

## ADRs (architecture decisions)

- **ADR-1: In-process MCP client for the default run.** Rationale: keeps
  `uv run python -m copthief.main` fast, offline-capable, and free of port
  conflicts, while `Client(fastmcp_app)` still exercises the real MCP tool
  contract. Trade-off: doesn't prove real network transport by itself — the
  two-process mode (`cop_server.py`/`thief_server.py`) covers that.
- **ADR-2: LLM only for the message/action layer, Q-learning for the
  optimizer.** Rationale: satisfies both the exercise's "free natural
  language" requirement and its recommended Table-Q algorithm, without
  requiring network access for automated tests (offline template fallback
  mirrors the same Q-table-driven action).
- **ADR-3: One `Agent` class parameterized by `Role`, not two subclasses.**
  Rationale: cop/thief decision logic is identical except for the action
  space and prompt flavor text — subclassing would duplicate the `decide()`
  Template Method per the anti-duplication rule in the submission
  guidelines.

## API / data contracts

- MCP tool `take_turn(partial_view: dict, incoming_message: str, legal_actions: list[str]) -> {message: str, action: str}`.
- MCP tool `report_outcome(reward: float, next_partial_view: dict, done: bool) -> {acknowledged: bool}`.
- `internal_game_report` JSON — see `docs/PRD.md`.
