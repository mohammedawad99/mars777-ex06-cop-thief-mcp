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
- [x] Live-readiness preflight ready (`deployment.live_readiness` exits 0, lists
      blockers; read-only — no live send, no deploy)
- [x] Gmail OAuth files present **outside the repo** (manual smoke: draft + calendar
      event OK); `gmail.preflight` → `status: ready` without reading file contents
- [x] Cloud live blockers cleared: `gcloud` installed + authenticated, project
      `api-mars-777` active, **billing enabled**, region `me-west1` confirmed
- [x] Two MCP services **deployed** at public, app-token-authenticated Cloud Run
      URLs (`mars777-cop-mcp`, `mars777-thief-mcp` in `api-mars-777`/`me-west1`)
- [x] Public HTTPS smoke passed: both reject a bad token, accept the correct token
      (`scripts/public_cloud_smoke.py` → `passed: true`)
- [x] Sanitized deployment evidence committed, no token values
      (`results/evidence/cloud_deployment.example.json`)
- [x] Cop & Thief public URLs recorded in README + evidence; tokens only in
      git-ignored `.secrets/` (never committed/printed)
- [x] Real `cop_mcp_url`/`thief_mcp_url` recorded in tracked evidence + README
      (deployed-state in `results/evidence/cloud_deployment.example.json`;
      `config/cloud.default.json` deliberately stays the not-deployed packaging
      template so the packaging preflight remains a valid pre-deploy gate)
- [x] Full **6-sub-game game over the public `/mcp` URLs** + official report built
      and **schema-validated** (`scripts/public_cloud_final_dry_run.py`;
      `results/evidence/public_cloud_full_game.example.json`)
- [x] Final official report **Gmail dry-run** passed with that report (`dry_run`,
      `body_json_valid: true`); **no live email sent**
      (`results/evidence/final_report_dry_run.example.json`)
- [x] Official report supports the **two real students** (MaRs-777) at runtime; real
      identities load from a local **git-ignored** file (`.secrets/students.local.json`)
- [x] Tracked evidence **redacts** student national IDs (`id: REDACTED` + privacy
      flags); no national-ID value in any tracked file
      (`results/evidence/public_cloud_full_game.example.json`)
- [x] **Git history scrubbed** of student national IDs (`git filter-repo` +
      `--force-with-lease`); all reachable history ID-free, verified in a fresh
      clone (0 matches); repo stayed public (GitHub internal-cache caveat noted)
- [x] Gmail **draft preview** of the official JSON report created (to the student's
      own account, **not** the lecturer); subject `PREVIEW ONLY - …`; JSON-only body,
      schema-valid, no placeholders; **not sent** (`scripts/gmail_draft_preview.py`,
      `results/evidence/gmail_draft_preview.example.json`) — this is a preview, **not**
      the official submission
- [ ] Real internal report emailed **to the lecturer** via `RUN_GMAIL_LIVE=1` with
      external OAuth files (optional live send; not run yet)
- [x] Inter-group bonus **readiness gate** prepared (`bonus_partner_readiness.py`):
      self cloud ready, local partner intake + strategy, sanitized evidence
      (`bonus_ready: false` pending partner; no tokens/IDs) — **prepared, not the game**
- [ ] Real inter-group bonus game played and reconciled (Stage 15B)

## Documentation & measurement
- [ ] PRDs, PLAN, DECISIONS, PROMPTS complete and current
- [ ] COSTS includes measured (not just assumed) figures
- [ ] QUALITY gates documented and reproducible
- [ ] `FINAL_GAP_AUDIT.md` completed and closed

## Process
- [ ] No `git add .` used; staging was explicit
- [ ] Commits made only after review
