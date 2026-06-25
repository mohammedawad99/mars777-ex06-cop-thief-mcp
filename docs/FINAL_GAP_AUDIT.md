# FINAL GAP AUDIT

> **CLOSED (Stage 15G).** This audit is finalized for the delivered in-repo scope of
> Assignment 6. Remaining items are **external** (the Moodle submission form) and
> **post-grading cleanup** (token revocation, optional Cloud Run teardown). All quality
> gates pass (401 tests, 100% coverage); no tokens or student national IDs are committed.

## Purpose

A last-mile, adversarial pass that compares the delivered system against the
PRDs, the assignment rubric, and `SUBMISSION_CHECKLIST.md`, and records every
remaining gap with a disposition (fixed / accepted / deferred).

## Audit dimensions (finalized — Stage 15G)

| Dimension | Expected | Actual | Gap | Disposition |
|-----------|----------|--------|-----|-------------|
| Game rules correctness | per PRD §5 | grid/8-dir/diagonal/capture/scoring engine, 100% tested | none | ✅ fixed |
| MCP over HTTP + token auth | per PLAN §5 | two Cloud Run services, app-token auth, public smoke `passed` | none | ✅ fixed |
| NL protocol conformance | per protocol PRD | free-text messages + role-safe observations; no hidden-state leak | none | ✅ fixed |
| Agents play end-to-end | per PRD AC3 | prompted/observed agents play full games over MCP | none | ✅ fixed |
| Orchestrator aggregation | per PRD FR6 | `num_sub_games` runner + totals; bonus referee canonical | none | ✅ fixed |
| Report sender delivery | per PRD FR8 | JSON-only Gmail sender; **bonus_game sent live** to lecturer | none | ✅ fixed |
| Bonus inter-group | per bonus PRD | official 6-sub-game match, mutually agreed, hash matched | none | ✅ fixed |
| Quality gates green | per QUALITY | ruff/format clean, 401 tests, 100% coverage, hardened smoke ok | none | ✅ fixed |
| Security / secrets | per SECURITY | no tokens/OAuth/IDs committed; OAuth external; redaction enforced | none | ✅ fixed |
| Costs measured | per COSTS | deterministic agents → no real LLM spend; live Gemini opt-in | real-LLM figures N/A | ➖ accepted |
| Partner matching send | mutual confirm | orcai-mj confirmed they sent their matching `bonus_game` report | none | ✅ fixed |
| internal_game live email | optional | built/validated, dry-run + student-only draft; not live-sent (by design) | not sent | ➖ accepted |
| Moodle submission form | external | repo public + documented | human step | ⏳ deferred (external) |
| Token revocation / cleanup | post-grading | documented instructions only | not yet done | ⏳ deferred (post-grading) |

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
| Official bonus board size | **frozen 8x8** by mutual written agreement (Stage 15D); thief-first, 6 sub-games, ≤25 moves, ≤5 cop-only barriers, diagonal, 0-based `[row,col]` | Done (Stage 15D) |
| Real inter-group bonus game | **played** — automated referee ran the official 6-sub-game match vs orcai-mj on 8x8 (both directions, no human moves); 6/6 decided; totals MaRs-777 30 / orcai-mj 90; canonical `bonus_game` JSON + token-free handoff with `result_hash` (`validation_status: valid`) | Done (Stage 15D) |
| Bonus mutual agreement | **finalized** — partner orcai-mj confirmed the result and rules in writing; `mutual_agreement: true`, `partner_confirmation_status: confirmed`, `bonus_claim: true` (result fields untouched; `result_hash` unchanged `a0fdf72d…`); final handoff ships a derived `hash_method` the partner can reproduce | Done (Stage 15E) |
| Bonus_game Gmail report | **sent live** — exactly one JSON-only `bonus_game` email (with top-level `result_hash a0fdf72d…`) sent to the lecturer (Stage 15F); partner independently reproduced + matched the hash and is sending their matching report; `live_gmail_sent: true`, `bonus_email_sent: true`, `internal_game_sent: false`; idempotency guard blocks duplicates; body ID-redacted | Done (Stage 15F) |
| Our agents on the official 8x8 board | **known weakness** — deployed servers were provisioned for the 5x5 visibility config, so our agents play weaker on 8x8 (far-edge moves defer to the engine's documented legal fallback); orcai-mj won 6/0. The real, autonomous outcome — disclosed, not faked | Accepted (honest disclosure) |
| Bonus report sent live to the lecturer | **sent** — one live `bonus_game` Gmail to the lecturer (Stage 15F); partner sending their matching report | Done (Stage 15F) |
| `internal_game` report sent live to the lecturer | **not sent** — only dry-run + a student-only draft preview; the live internal-report send is opt-in and still pending (not part of Stage 15F) | Deferred |
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
