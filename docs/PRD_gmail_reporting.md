# PRD — Gmail API Game-Report Sending

## Theoretical background

The exercise recommends emailing the final `internal_game_report` JSON to
the course address via the Gmail API (OAuth), rather than SMTP + a stored
password, to avoid keeping long-lived credentials in the repo.
`src/copthief/reporting/gmail_sender.py` implements the standard
Google "installed app" OAuth flow: a one-time interactive browser consent
produces a refreshable token cached at `GMAIL_TOKEN_PATH`.

## Requirements: input/output, performance targets

- Input: the `internal_game_report` dict (from `json_report.py`) and a
  recipient address (`config.json: report_recipient`).
- Output: the Gmail API `messages.send` response dict.
- Rate limit: 5 requests/min, 50/hour (`config/rate_limits.json`, service
  `"gmail"`), enforced by the same `ApiGatekeeper` used for LLM calls.

## One-time setup required before real sending (not done in this session)

1. In Google Cloud Console, enable the Gmail API for a project and create
   an OAuth 2.0 **Desktop app** client; download `credentials.json`.
2. Set `GMAIL_CREDENTIALS_PATH=/path/to/credentials.json` in `.env`.
3. Run any script that calls `GmailSender.send_report(...)` once,
   interactively, from a machine with a browser — this performs the OAuth
   consent and writes the refresh token to `GMAIL_TOKEN_PATH`.
4. Subsequent calls (including from a headless environment) reuse the
   cached, auto-refreshed token.

This flow requires the student's own Google account and browser access, so
it was **implemented and unit-tested with a mocked `googleapiclient` client
only** — it was not executed against a real account in this build.

## Constraints, trade-offs, rationale

- No API key/token is ever hardcoded; both paths come from `.env`
  (`.env-example` documents the two variables), and `.gitignore` excludes
  `.env`, `credentials.json`, and the cached token file.
- `GmailNotConfiguredError` is raised (not swallowed) when credentials are
  missing, so a misconfigured environment fails loudly rather than silently
  skipping the report email.

## Success criteria and specific test scenarios

- `tests/unit/reporting/test_gmail_sender.py`: `send_report` raises
  `GmailNotConfiguredError` when `GMAIL_CREDENTIALS_PATH` is unset; with a
  mocked `_build_service`, `send_report` builds a correctly base64-encoded
  MIME message and calls `messages().send()` exactly once, routed through
  the gatekeeper (verified via a call counter).
