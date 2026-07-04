# Task Tracking

## Phase 1 — Foundation (done)
- [x] `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` approved before coding.
- [x] `config/config.json`, `config/rate_limits.json`.
- [x] `shared/{config,constants,version,gatekeeper}.py`.

## Phase 2 — Game engine (done)
- [x] `game/grid.py` — grid + barrier placement.
- [x] `game/state.py` — GameState + partial-observability view.
- [x] `game/rules.py` — legal actions, apply_action, capture check.
- [x] `game/scoring.py` — config-driven scoring table.

## Phase 3 — Agents (done)
- [x] `agents/q_learning.py` — tabular Q-learning, Bellman update.
- [x] `agents/llm_client.py` — Anthropic wrapper via gatekeeper.
- [x] `agents/nl_protocol.py` — prompt builder, reply parser, offline fallback.
- [x] `agents/base_agent.py` — single parameterized Agent (Template Method).

## Phase 4 — MCP layer (done)
- [x] `mcp_servers/factory.py` — shared FastMCP server builder.
- [x] `mcp_servers/cop_server.py`, `mcp_servers/thief_server.py`.

## Phase 5 — Orchestration & SDK (done)
- [x] `orchestrator/sub_game.py` — one episode, technical-loss handling.
- [x] `orchestrator/game_series.py` — 6-episode series with retry.
- [x] `sdk/sdk.py` — single facade, `main.py` CLI entry point.

## Phase 6 — Reporting & GUI (done)
- [x] `reporting/json_report.py` — `internal_game_report` builder.
- [x] `reporting/gmail_sender.py` — OAuth send (documented, mocked in tests).
- [x] `gui/console_view.py` — ASCII transcript + matplotlib plot.

## Phase 7 — Quality gates (in progress)
- [x] Unit tests per module + graduated sanity checks (2x2 → 5x5).
- [x] `uv run pytest --cov` — 50 tests, 93% coverage (≥85% gate passed).
- [x] `uv run ruff check .` — zero violations.
- [x] Pushed to `https://github.com/afaf-gharra/marl-cop-thief` (public).
- [x] Drafted (not sent) the `game_report.json` submission email — see
      `results/draft_email.eml`, built by
      `scripts/build_draft_email.py` without touching the Gmail API.

## Phase 8 — Left to the student (out of this session's scope)
- [ ] Real Prefect Cloud / ngrok deployment of both MCP servers.
- [ ] Real Gmail OAuth consent + actually sending
      `results/draft_email.eml` via `gmail_sender.send_report(...)`.
- [ ] Bonus inter-group race, if a partner team is found.
