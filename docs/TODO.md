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
- [x] `gui/console_view.py` — ASCII transcript + static matplotlib plot.
- [x] `gui/animation.py` — real-time-style per-sub-game animated GIF
      (`render_sub_game_gif`) plus a best-effort live window
      (`render_live_window`) for machines with a display.

## Phase 7 — Quality gates (done)
- [x] Unit tests per module + graduated sanity checks (2x2 → 5x5).
- [x] `uv run pytest --cov` — 68 tests, 92% coverage (≥85% gate passed).
- [x] `uv run ruff check .` — zero violations; all files ≤150 lines.
- [x] Pushed to `https://github.com/afaf-gharra/marl-cop-thief` (public).

## Phase 8 — Real integrations (executed)
- [x] **Real LLM dialogue**: full 6-game series through OpenAI `gpt-4o-mini`
      (`assets/llm_run_log.txt`, cost ~$0.006/series in the notebook).
- [x] **Real cloud deployment**: both MCP servers on AWS EC2 with Bearer-token
      auth + a locked-down security group; a 6-game series played over the
      public internet; resources torn down in the same session. Evidence:
      `assets/cloud_run_log.txt`, `assets/cloud_auth_proof.txt`,
      `assets/demo_cloud_game_report.json`; record in `docs/PLAN.md`.
- [x] **Research notebook** with executed outputs + figures (`assets/*.png`).
- [x] **Gmail send** — OAuth consent completed; the cloud-run report was
      emailed to `rmisegal+uoh26b@gmail.com` via the Gmail API
      (`uv run python -m copthief.reporting.send_report`, message id
      `19f36657f46ff3b8`). Body is the JSON report only, per spec.

## Out of scope
- [ ] Bonus inter-group race — needs a partner team; schema + builder ready
      (`build_bonus_game_report`), no live cross-group match played.
- [ ] Moodle submission PDF (`SMNGRP05-ex06.pdf`) — no Word template available.
