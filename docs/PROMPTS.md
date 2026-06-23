# PROMPTS — AI Collaboration Log

This file records the prompts that materially shaped the repository, per the
course's vibe-coding documentation requirement.

## Stage 0 — Initial skeleton prompt (2026-06-23)

**Goal:** Establish a 100-level foundation for Assignment 6 (Dual AI Agent
Cop-and-Thief via MCP) — repository skeleton, documentation scaffolding,
configuration, packaging, and quality gates only. **No** game engine, MCP
server, or Gmail implementation yet. Bonus inter-group play treated as
mandatory scope for architecture.

**Key constraints captured from the prompt:**
- Python with **uv only** (no pip / `python -m` / requirements.txt / venv).
- Professional `src/` package; every source file < 150 logical lines.
- No secrets; strict `.gitignore`; `.env-example` placeholders only.
- `pyproject.toml` with pytest, coverage `fail_under = 85`, ruff.
- Minimal placeholder code so imports and tests pass.
- Required docs, config, src, and tests files as enumerated.
- Do **not** run `git add .`; do **not** commit until instructed.

**Outcome:** Stage 0 skeleton created with SDK façade, shared version/config,
default JSON configs, full docs drafts, and three passing unit-test modules.

## Stage 1 — Requirements hardening & architecture planning (2026-06-23)

**Goal:** Produce a strict Requirements Matrix and supporting planning documents
for a 100-level submission in which the inter-group bonus is treated as
**mandatory scope**. Planning and documentation only — **no** game engine, MCP
server, agent, or Gmail implementation; no new dependencies; no commit.

**Key constraints captured from the prompt:**
- Encode the full assignment fact set: two agents (Cop/Thief), two MCP servers,
  free natural-language comms, **HTTP MCP from day one**, local self-play, cloud
  via public authenticated URLs, inter-group bonus as mandatory scope, two URLs
  per team protected by token/auth.
- Game rules: turn-based, default 5×5, config-driven params, sanity grids
  2×2→5×5, 6 sub-games × ≤25 moves, capture on shared cell, Thief wins on
  survival, 8-direction movement, no stay unless negotiated, Cop barriers ≤5,
  Thief no barriers, barriers block both, illegal moves detected/logged.
- Scoring (Cop-win 20/5, Thief-win 10/5), team totals bounded `[30, 90]`.
- JSON-only reports and JSON-only instructor email body; internal and bonus
  report field sets; `mutual_agreement` gate for the bonus.
- Security: OAuth/token outside Git, no open endpoints, Gmail API preferred.
- Professional practices and prior Assignment 1 feedback (planning docs, visible
  prompts, cost awareness, quality, extensibility, evidence-backed claims).

**Artifacts produced:**
- `docs/REQUIREMENTS_MATRIX.md` — 70 requirements (R-001…R-070) with priority,
  proof artifact, validation method, risk, status.
- `docs/ACCEPTANCE_CRITERIA.md` — measurable criteria across 10 delivery areas.
- `docs/RISK_REGISTER.md` — 24 risks with impact/likelihood/mitigation/trigger/
  owner (incl. all required named risks).
- `docs/INTERGROUP_BONUS_PROTOCOL.md` — operational coordination procedure,
  explicitly not a hardcoded agent wire protocol.
- Updates to `PLAN.md` (matrix + interop + evidence plan), `DECISIONS.md`
  (ADR-0007…ADR-0011), `TODO.md` (Stage 1 inserted, stages renumbered).

**Outcome:** Requirements hardening complete; baseline established for the
engine stage. No implementation added; no commit made.

> Subsequent stages will append their driving prompts here (engine, MCP,
> protocol, agents, orchestrator, report sender, cloud, bonus, audit).
