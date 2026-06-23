# PRD — Google Report Sender

**Status:** Stage 0 draft (not yet implemented)

## Purpose

After the orchestrator completes `num_sub_games`, send a results report by email
using Google/Gmail, to `report_recipient`.

## Inputs

- Aggregated results: per-sub-game outcomes, scores, totals, seed, timestamps
  (in `Asia/Jerusalem`), and a summary line.

## Auth & credentials

- Google **OAuth** user flow. Client secrets (`credentials.json`) and the issued
  token (`token.json`) are **kept outside Git** and referenced via env vars
  (`GOOGLE_OAUTH_CLIENT_SECRETS`, `GOOGLE_OAUTH_TOKEN_PATH`).
- First run performs interactive consent; subsequent runs reuse the stored
  token. Revoke story documented in `SECURITY.md`.

## Behavior

- Compose a clear, plain-text (optionally HTML) report.
- Send to `REPORT_RECIPIENT` / config `report_recipient`.
- On failure: retry with backoff (bounded), log redacted errors, and surface a
  non-zero exit so the run is not silently considered successful.

## Testing

- Unit tests mock the Gmail client; **no real emails** are sent and **no
  credentials** are required in tests. A manual, opt-in live check is documented
  separately and never part of CI.

## Acceptance

- Given aggregated results and valid local credentials, a correctly formatted
  report is delivered; tests pass without network or secrets.
