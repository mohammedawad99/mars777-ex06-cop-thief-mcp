# FINAL GAP AUDIT

> **This audit is NOT final yet.** It is a living placeholder maintained through
> development and **completed near submission**. Do not treat any statement here
> as a final verdict until this banner is removed.

## Purpose

A last-mile, adversarial pass that compares the delivered system against the
PRDs, the assignment rubric, and `SUBMISSION_CHECKLIST.md`, and records every
remaining gap with a disposition (fixed / accepted / deferred).

## Audit dimensions (to be filled near submission)

| Dimension | Expected | Actual | Gap | Disposition |
|-----------|----------|--------|-----|-------------|
| Game rules correctness | per PRD §5 | — | — | — |
| MCP over HTTP + token auth | per PLAN §5 | — | — | — |
| NL protocol conformance | per protocol PRD | — | — | — |
| Agents play end-to-end | per PRD AC3 | — | — | — |
| Orchestrator aggregation | per PRD FR6 | — | — | — |
| Report sender delivery | per PRD FR8 | — | — | — |
| Bonus inter-group | per bonus PRD | — | — | — |
| Quality gates green | per QUALITY | — | — | — |
| Security / secrets | per SECURITY | — | — | — |
| Costs measured | per COSTS | — | — | — |

## Current status (through Stage 13A)

The local pipeline is implemented, tested (100% coverage), and hardened
(deterministic run identity/manifest, classified failures, bounded
retries/timeouts, aggregate report validation). The following are **honestly
known open gaps**, deferred to later stages — none is claimed as done:

| Gap | Status | Disposition |
|-----|--------|-------------|
| Cloud deployment packaging & preflight | **present** — Dockerfile, role entrypoint, cloud config, preflight (`status: ok`) | Done (Stage 13A) |
| Real deployed public URLs | **still missing** — `cloud_status: not_deployed`, placeholder URLs; no Cloud Run service created | Deferred (Stage 13B, gated) |
| Live Gmail send | **not sent** — dry-run only; live is opt-in (`RUN_GMAIL_LIVE=1`) with external OAuth files | Deferred (opt-in local) |
| Live Gemini provider run | **not run** — offline `fake_local` default; live is opt-in (`RUN_GEMINI_LIVE=1`) with a key | Deferred (opt-in local) |
| Real inter-group bonus game | **not completed** — bonus schema/protocol exist; no real cross-group match played | Deferred (Stage 14) |
| Final Moodle submission PDF | **not prepared yet** | Deferred (near submission) |
| Measured real LLM/Gmail cost | **TBD** — fake/dry-run only; real figures pending a live run | Deferred (after a live run) |

Already in place and evidenced: game engine + rules, partial observability,
local MCP over HTTP with token auth, fake-local prompted MCP full game over HTTP,
official validated JSON report + sanitized evidence pack, Gmail JSON-only sender
(dry-run), optional Gemini adapter (gated), the Stage 12 hardened run manifest +
aggregate validation, and Stage 13A cloud deployment **packaging + preflight** (no
live deploy). The dimension table below is finalized near submission once the
deferred items are addressed or formally accepted.
