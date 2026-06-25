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

## Current status (through Stage 14A)

The local pipeline is implemented, tested (100% coverage), and hardened
(deterministic run identity/manifest, classified failures, bounded
retries/timeouts, aggregate report validation). The following are **honestly
known open gaps**, deferred to later stages — none is claimed as done:

| Gap | Status | Disposition |
|-----|--------|-------------|
| Cloud deployment packaging & preflight | **present** — Dockerfile, role entrypoint, cloud config, preflight (`status: ok`) | Done (Stage 13A) |
| Live-readiness preflight | **present** — `deployment.live_readiness` combines Gmail OAuth + read-only cloud/gcloud + packaging; exits 0, lists blockers; no live send/deploy | Done (Stage 13B) |
| Gmail OAuth files (external) | **present outside the repo** — manual smoke succeeded (Gmail draft + Calendar event); `gmail.preflight` → `ready` (no content read); never committed | Done (manual, external) |
| Cloud live deployment | **done** — both MCP services deployed to Cloud Run (`api-mars-777`/`me-west1`); public HTTPS smoke `passed: true`; APIs enabled: run/cloudbuild/artifactregistry | Done (Stage 13C) |
| Real deployed public URLs | **present** — `mars777-cop-mcp` + `mars777-thief-mcp` live; recorded in `results/evidence/cloud_deployment.example.json` and README (no token values) | Done (Stage 13C) |
| Full public-cloud game + official report | **done** — 6/6 sub-games over the public `/mcp` URLs; official report schema-valid; Gmail **dry-run** passed (no send); token-free evidence | Done (Stage 14A) |
| Official report student identities | **runtime-only** — two MaRs-777 students load from a local git-ignored file at runtime; the in-memory report + Gmail dry-run use real IDs | Done (Stage 14A/14B) |
| Student national-ID privacy in tracked files | **redacted** — no national-ID value in any tracked file; tracked evidence shows `id: REDACTED` + `identity_privacy` flags | Done (Stage 14B hotfix) |
| Student national-ID privacy in Git history | **scrubbed** — `git filter-repo` rewrote history (IDs → `REDACTED_STUDENT_ID`); `git push --force-with-lease`; **all reachable history is ID-free**, verified in a fresh clone (0 matches). Repo stayed public | Done (Stage 14B history scrub) |
| Gmail draft preview of official report | **created** — Gmail **draft** (not sent) of the official JSON report to the student's own account (not lecturer); JSON-only, schema-valid, no placeholders; sanitized evidence (no IDs) | Done (Stage 14C) |
| Final official report sent to lecturer via Gmail | **not sent** — only dry-run + a student-only draft preview done; live send to the lecturer is opt-in (`RUN_GMAIL_LIVE=1`) and still pending | Deferred (Stage 14D) |
| Live Gemini provider run | **not run** — offline `fake_local` default; live is opt-in (`RUN_GEMINI_LIVE=1`) with a key | Deferred (opt-in local) |
| Inter-group bonus readiness | **prepared** — readiness gate validates self cloud (ready) + partner intake/compat smoke; local partner file + strategy in place; `bonus_ready: false` pending real partner | Done (Stage 15A) |
| Partner interop adapter (orcai-mj) | **confirmed live** — adapter reconciled to the partner's real `setup`/`observe`/`my_move`/`state` contract (token key `token`; `setup` carries 0-based `cop`/`thief` starts + `rows`/`cols`/`origin`/`diagonal`; `observe(message,mover,token)`; `my_move(token)`), tested; the Stage 15B provisional keys were wrong | Done (Stage 15C) |
| Live partner compatibility smoke | **passed** — `bonus_partner_live_smoke.py` against the partner's live `/mcp` endpoints: unauthorized rejected, authorized accepted, setup/observe/my_move/state OK, role identity consistent per server, 0-based `[row,col]`, thief-first, **5x5 + 8x8** warm-ups pass (`partner_smoke_passed: true`); sanitized token-free evidence | Done (Stage 15C) |
| Official bonus board size | **recommended 5x5** (our baseline; both 5x5/8x8 work) — **not frozen**; mutual written agreement pending | Deferred (Stage 15D) |
| Real inter-group bonus game | **not completed** — compatibility confirmed but no official 6-sub-game match played yet; `bonus_game` report not produced | Deferred (Stage 15D) |
| Final Moodle submission PDF | **not prepared yet** | Deferred (near submission) |
| Measured real LLM/Gmail cost | **TBD** — fake/dry-run only; real figures pending a live run | Deferred (after a live run) |

Already in place and evidenced: game engine + rules, partial observability,
local MCP over HTTP with token auth, fake-local prompted MCP full game over HTTP,
official validated JSON report + sanitized evidence pack, Gmail JSON-only sender
(dry-run), optional Gemini adapter (gated), the Stage 12 hardened run manifest +
aggregate validation, Stage 13A cloud deployment **packaging + preflight** (no
live deploy), Stage 13B **live-readiness preflight** (read-only Gmail OAuth +
cloud/gcloud checks), Stage 13C **live Cloud Run deployment** of both MCP
services at public token-auth URLs with a passing public HTTPS smoke, and Stage 14A
a **full public-cloud 6-sub-game game + official report dry-run** (schema-valid
report; Gmail dry-run; token-free evidence), and the Stage 14B **privacy hotfix**
(student national-IDs removed from all tracked files; loaded at runtime from a local
git-ignored file; tracked evidence redacted). Still **not** done: **no live Gmail
report sent**, **no real inter-group bonus match**, and **no final submission** —
these remain Stage 14C+. The dimension table below is finalized near submission once
the deferred items are addressed or formally accepted.
