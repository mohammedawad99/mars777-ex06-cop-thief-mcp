# TODO — Staged Milestones

Statuses: ✅ done · 🔄 in progress · ⏳ planned

| Stage | Milestone | Status |
|------|-----------|--------|
| 0 | Repo skeleton: package layout, docs scaffolding, config defaults, packaging, quality gates | ✅ |
| 1 | Game engine: grid, 8-dir movement, barriers, capture, scoring, deterministic stepping + unit tests | ⏳ |
| 2 | MCP servers (HTTP, token auth): perception/action tools mapped to engine | ⏳ |
| 3 | Natural-language protocol: agent↔server message schema + parser/validator | ⏳ |
| 4 | Cop & Thief LLM agents wired through MCP | ⏳ |
| 5 | Orchestrator: run num_sub_games, seeds, aggregation, rate limits | ⏳ |
| 6 | Google report sender (Gmail/OAuth) for final results | ⏳ |
| 7 | Bonus inter-group play against another group's server | ⏳ |
| 8 | Hardening: cost/measurement tracking, logging, security review | ⏳ |
| 9 | Final gap audit + submission checklist closure | ⏳ |

## Stage 0 checklist (current)

- [x] `pyproject.toml` with pytest, coverage (fail_under=85), ruff
- [x] `src/` package with SDK, shared version/config, constants
- [x] `config/*.default.json` (game, rate_limits, logging)
- [x] `docs/` drafts (PRDs, PLAN, DECISIONS, QUALITY, COSTS, SECURITY, …)
- [x] `.gitignore`, `.env-example`
- [x] Minimal tests (version, config, SDK smoke) passing via uv
- [ ] Reviewed and explicitly committed (held until instructed)

## Next up (Stage 1)

- [ ] Define engine data types (position, board, state) in SDK
- [ ] Implement movement + barrier collision rules
- [ ] Implement capture detection and scoring
- [ ] Unit tests for all sanity grid sizes (2×2…5×5)
