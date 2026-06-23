# TODO — Staged Milestones

Statuses: ✅ done · 🔄 in progress · ⏳ planned

| Stage | Milestone | Status |
|------|-----------|--------|
| 0 | Repo skeleton: package layout, docs scaffolding, config defaults, packaging, quality gates | ✅ |
| 1 | Requirements hardening & architecture planning: Requirements Matrix, acceptance criteria, risk register, inter-group protocol, plan/ADR updates | ✅ |
| 2 | Game engine: grid, 8-dir movement, barriers, capture, scoring, deterministic stepping + unit tests | ⏳ |
| 3 | MCP servers (HTTP, token auth): perception/action tools mapped to engine | ⏳ |
| 4 | Natural-language protocol: agent↔server message interpretation + validator + interpreted-action logs | ⏳ |
| 5 | Cop & Thief LLM agents wired through MCP | ⏳ |
| 6 | Orchestrator: run num_sub_games, seeds, aggregation, rate limits | ⏳ |
| 7 | Google report sender (Gmail/OAuth) for final results, JSON-only email body | ⏳ |
| 8 | Cloud/self-play through public, authenticated URLs | ⏳ |
| 9 | Bonus inter-group play against another group's server (mandatory scope) | ⏳ |
| 10 | Hardening: cost/measurement tracking, logging, security review | ⏳ |
| 11 | Final gap audit + submission checklist closure | ⏳ |

## Stage 0 checklist (current)

- [x] `pyproject.toml` with pytest, coverage (fail_under=85), ruff
- [x] `src/` package with SDK, shared version/config, constants
- [x] `config/*.default.json` (game, rate_limits, logging)
- [x] `docs/` drafts (PRDs, PLAN, DECISIONS, QUALITY, COSTS, SECURITY, …)
- [x] `.gitignore`, `.env-example`
- [x] Minimal tests (version, config, SDK smoke) passing via uv
- [ ] Reviewed and explicitly committed (held until instructed)

## Stage 1 checklist (completed — requirements hardening)

- [x] `docs/REQUIREMENTS_MATRIX.md` — audit backbone (70 requirements, R-001…R-070)
- [x] `docs/ACCEPTANCE_CRITERIA.md` — measurable criteria across 10 areas
- [x] `docs/RISK_REGISTER.md` — 24 risks with mitigation/trigger/owner
- [x] `docs/INTERGROUP_BONUS_PROTOCOL.md` — operational (not wire) protocol
- [x] `docs/PLAN.md` — matrix as verification artifact + evidence plan + interop
- [x] `docs/DECISIONS.md` — ADRs for matrix, bonus scope, NL+interpreted logs,
      operational protocol separation, evidence-first delivery
- [x] `docs/PROMPTS.md` — Stage 1 prompt summary appended
- [x] Reviewed and explicitly committed

## Next up (Stage 2 — game engine)

- [ ] Define engine data types (position, board, state) in SDK
- [ ] Implement movement + barrier collision rules
- [ ] Implement capture detection and scoring
- [ ] Unit tests for all sanity grid sizes (2×2…5×5)
