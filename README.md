# Cop/Thief — Dual AI Agent Race via MCP Servers

Ex06 (bonus), team code **SMNGRP05** — afaf gharra (ID 208123232).

Two independent AI agents — a **Cop** and a **Thief** — hunt/evade each other
on a grid. Each agent is backed by its own **FastMCP server** and can only
learn about the other through **free natural-language messages**; there is
no shared memory or direct function call between them. See
[`docs/PRD.md`](docs/PRD.md) and [`docs/PLAN.md`](docs/PLAN.md) for the full
design, and [`docs/PRD_mcp_protocol.md`](docs/PRD_mcp_protocol.md) /
[`docs/PRD_q_learning.md`](docs/PRD_q_learning.md) for the two core
mechanisms.

## Installation

Requirements: Python 3.11+, [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
cp .env-example .env   # optional: set ANTHROPIC_API_KEY for live LLM dialogue
```

Common setup issues:
- **No `ANTHROPIC_API_KEY`**: agents automatically fall back to an offline,
  deterministic message template — the game still runs end-to-end.
- **Port already in use**: the standalone server scripts bind
  `127.0.0.1:8801` (cop) and `127.0.0.1:8802` (thief); change
  `COP_MCP_PORT`/`THIEF_MCP_PORT` in `src/copthief/shared/constants.py` if
  those ports are taken.

## Usage

Run a full 6-sub-game series locally (both MCP servers are started
in-process, no ports needed for this default mode):

```bash
uv run python -m copthief.main
```

This prints an ASCII transcript of each sub-game, the final cop/thief
totals, and writes `results/game_report.json` (schema in
`docs/PRD.md` §JSON report) plus `results/final_positions.png`.

To draft (but **not send**) the submission email from that report:

```bash
uv run python -m copthief.reporting.draft_email
```

This writes `results/draft_email.eml` (a standard, openable email file) with
the report as its body, addressed to `config.json: report_recipient` — no
Gmail API call is made. Review it, then send it yourself once
`GMAIL_CREDENTIALS_PATH` is configured (see
`docs/PRD_gmail_reporting.md`) via `GmailSender.send_report(...)`.

To run the two agents as genuinely separate HTTP processes (the
"two localhost servers on different ports" deployment stage from the
exercise spec), in two terminals:

```bash
uv run python -m copthief.mcp_servers.cop_server
uv run python -m copthief.mcp_servers.thief_server
```

Workflows / flags:
- `ANTHROPIC_API_KEY` set → agents use live LLM-generated free text.
- unset → offline template fallback (used for all automated tests/CI).
- `config/config.json` → grid size, move limit, number of sub-games, barrier
  limit, and the scoring table (see `docs/PLAN.md`).

## Examples and demos

A sample transcript looks like:

```
--- Sub-game 1: cop_wins ---
[thief] -> [2, 3] (right): Slipping away, heading right from [2, 2].
[  cop] -> [1, 3] (down): Closing in from [0, 3], moving down.
...
Score -> cop: 20, thief: 5
```

`results/final_positions.png` plots each sub-game's final cop (blue square)
and thief (red circle) position on the grid.

## Configuration guide

See `config/config.json` (`grid_size`, `max_moves`, `num_games`,
`max_barriers`, `scoring.*`) and `config/rate_limits.json`
(`requests_per_minute`, `requests_per_hour`, `concurrent_max`,
`retry_after_seconds`, `max_retries` per service: `default`, `llm`, `gmail`).
No gameplay or rate-limit values are hardcoded in source — see
`src/copthief/shared/config.py`.

## Contribution guidelines

Follow the repo's `ruff` config (`uv run ruff check .`), keep files ≤150
lines, write/extend tests before changing behavior (TDD), and update
`docs/TODO.md` as tasks progress. No secrets in source — use `.env`
(git-ignored) with `.env-example` documenting the required keys.

## Credits and license

MIT license (see `pyproject.toml`). Built with
[FastMCP](https://gofastmcp.com), [Anthropic Claude](https://www.anthropic.com),
NumPy, and Matplotlib. Course: bonus exercise ex06, Dr. Yoram Segal.

## Known limitations (honest self-assessment)

- **Cloud deployment** (Prefect Cloud / ngrok / ngrok-style tunneling) is
  documented in `docs/PLAN.md` but not actually deployed — it requires the
  student's own cloud accounts, out of scope for this sandboxed build.
- **Gmail sending** (`src/copthief/reporting/gmail_sender.py`) implements
  the full OAuth + send flow and is unit-tested with a mocked API client,
  but was never executed against a real Google account — see
  `docs/PRD_gmail_reporting.md` for the one-time setup a user must run.
- **Inter-group bonus race** (§12 of the exercise) needs a second team's
  MCP URLs, which don't exist for a solo submission; the JSON schema is
  supported (`report_type: "bonus_game"`) but no real cross-group match was
  played.
