# SUBMISSION CHECKLIST

Strict checklist for the final review. Boxes are checked only when verified.

## Repository & packaging
- [ ] `uv sync` succeeds from a clean checkout
- [ ] Professional `src/` package layout
- [ ] Every Python source file < 150 logical lines
- [ ] `pyproject.toml` configures pytest, coverage, ruff

## Quality gates
- [ ] `uv run pytest` passes
- [ ] Coverage ≥ 85% (`fail_under = 85`)
- [ ] `uv run ruff check .` clean
- [ ] `uv run ruff format --check .` clean
- [ ] `git status --short --ignored` shows no stray artifacts

## Security
- [ ] No secrets committed (`.env`, credentials, tokens, keys)
- [ ] `.gitignore` covers all secret/artifact patterns
- [ ] `.env-example` contains placeholders only
- [ ] MCP token auth enabled; OAuth files external; revoke story documented

## Functionality
- [ ] Game engine matches assignment rules (grid, movement, capture, scoring)
- [ ] MCP servers run over HTTP and expose perception/action tools
- [ ] Natural-language protocol implemented and validated
- [ ] Cop & Thief agents play through MCP
- [ ] Orchestrator runs `num_sub_games` and aggregates results
- [ ] Google report sender emails final results
- [ ] Bonus inter-group play demonstrated

## Documentation & measurement
- [ ] PRDs, PLAN, DECISIONS, PROMPTS complete and current
- [ ] COSTS includes measured (not just assumed) figures
- [ ] QUALITY gates documented and reproducible
- [ ] `FINAL_GAP_AUDIT.md` completed and closed

## Process
- [ ] No `git add .` used; staging was explicit
- [ ] Commits made only after review
