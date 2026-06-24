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

## Reports & evidence
- [x] Official internal report schema defined and **validated** (`reporting/`)
- [x] Report is JSON-only / email-body ready and **token-safe** (no token keys/values)
- [x] Bonus/inter-group schema example exists (no real run claimed; `bonus_claim=false`)
- [x] Sanitized, deterministic evidence pack committed under
      `results/evidence/*.example.json` (no tokens, no full event logs)
- [x] Optional real provider (Gemini) adapter implemented behind the LLM interface
      (opt-in; no key required for tests)
- [ ] Optional real-Gemini live smoke run locally with `RUN_GEMINI_LIVE=1` + key
      (evidence of real integration; not run in default validation)
- [x] Gmail JSON report sender implemented; dry-run validates + builds JSON-only
      body without sending (`uv run python -m mars777_cop_thief.gmail.send_report`)
- [x] Email body proven JSON-only (decodes/parses back to the report object)
- [x] Hardened run smoke passes with a secret-free manifest + aggregate validation
      (`uv run python -m mars777_cop_thief.run.hardened_smoke` → `status: ok`)
- [x] Deterministic `run_id`/config fingerprint; failures classified; bounded retries
- [x] Cloud deployment packaging + preflight ready (Dockerfile, role entrypoint,
      `deployment.preflight` → `status: ok`); no secrets in image
- [ ] Two MCP services deployed at public, authenticated URLs (manual gated deploy)
- [ ] `cloud_status` flipped + real `cop_mcp_url`/`thief_mcp_url` recorded locally
- [ ] Real internal report emailed via `RUN_GMAIL_LIVE=1` with external OAuth files
      (optional live send; not run in default validation)
- [ ] Real inter-group bonus game played and reconciled (later stage)

## Documentation & measurement
- [ ] PRDs, PLAN, DECISIONS, PROMPTS complete and current
- [ ] COSTS includes measured (not just assumed) figures
- [ ] QUALITY gates documented and reproducible
- [ ] `FINAL_GAP_AUDIT.md` completed and closed

## Process
- [ ] No `git add .` used; staging was explicit
- [ ] Commits made only after review
