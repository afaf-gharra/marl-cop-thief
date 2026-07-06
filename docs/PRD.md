# Product Requirements Document — Cop/Thief MCP Game

## Overview and context

Course exercise ex06 ("Dual AI Agent Conversation via MCP Servers").
The pedagogical goal (per the exercise spec) is not the win/loss result of
the game, but demonstrating that two fully autonomous AI agents can
coordinate complex, time-critical decisions over an unstructured natural
language channel, each backed by its own MCP server. Target audience: the
course grader; secondary audience: the student, for future reuse of the
MCP/Q-learning pattern.

## Goals and KPIs

- Two independent MCP servers (cop, thief) that only exchange free text.
- A full, valid 6-sub-game series completes without a crash (technical
  losses are retried).
- Coverage ≥85% on `src/` business logic (excludes `main.py`/`gui`).
- `ruff check .` passes with zero violations.
- Acceptance: `uv run python -m copthief.main` runs to completion offline
  (no API key) and produces `results/game_report.json` matching the spec's
  `internal_game_report` schema.

## Functional and non-functional requirements

**Functional**
- 5×5 (configurable) grid, thief moves first, turns alternate.
- Cop may place up to 5 barriers/sub-game; barriers block the thief and act
  like a wall for the cop.
- Cop wins on exact-cell capture; thief wins by surviving `max_moves` (25).
- Each turn: agent receives its own position + a coarse distance hint (not
  the opponent's exact cell) and the opponent's last free-text message, and
  must reply with a message plus one legal action.
- JSON report (`internal_game_report`) written after every series.

**Non-functional**
- No test may require network access or a live API key (offline template
  fallback).
- All gameplay/rate-limit constants are config-driven (`config/*.json`).
- SDK-layer entry point (`CopThiefSdk`) — no direct access to internals from
  CLI/tests.

## User stories

- As the grader, I can run one command and see two agents converse in free
  text and reach a scored outcome.
- As the student, I can swap the LLM for the offline fallback (unset the
  API key) and still demonstrate the full pipeline for grading without
  incurring API cost.

## Assumptions, dependencies, limitations

- Two-student group (SMNGRP05).
- Depends on `fastmcp`, `numpy`, `matplotlib`, `openai`, `anthropic`,
  `google-api-python-client` (see `pyproject.toml`).
- Limitation: cloud deployment and Gmail sending are implemented and
  documented but not executed live (see README "Known limitations").

## Timeline and milestones

1. Game engine + rules (done).
2. MCP servers + NL protocol + Q-learning (done).
3. Orchestrator + SDK + reporting (done).
4. Tests + docs + tooling (done).
5. Optional, user-run: push to GitHub, real cloud deploy, real Gmail send.

## internal_game_report JSON schema

```json
{
  "group_name": "SMNGRP05",
  "students": ["Afaf Gharra (208123232)", "Reem Awawdy (212018899)"],
  "github_repo": "https://github.com/afaf-gharra/marl-cop-thief",
  "cop_mcp_url": "http://127.0.0.1:8801",
  "thief_mcp_url": "http://127.0.0.1:8802",
  "timezone": "Asia/Jerusalem",
  "sub_games": [
    {"outcome": "cop_wins", "cop_points": 20, "thief_points": 5, "num_turns": 7, "transcript": ["..."]}
  ],
  "totals": {"cop": 90, "thief": 40}
}
```
