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

> Subsequent stages will append their driving prompts here (engine, MCP,
> protocol, agents, orchestrator, report sender, bonus, audit).
