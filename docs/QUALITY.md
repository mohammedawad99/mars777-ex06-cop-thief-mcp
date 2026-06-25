# QUALITY — Gates & Checks

All gates run locally via uv before any commit. A change is "green" only when
every gate below passes.

## Gates

1. **Dependency sync** — `uv sync`
2. **Tests** — `uv run pytest`
3. **Coverage (≥ 85%)** — `uv run pytest --cov=src --cov-report=term-missing`
   (enforced by `fail_under = 85` in `pyproject.toml`)
4. **Lint** — `uv run ruff check .`
5. **Format check** — `uv run ruff format --check .`
6. **Working tree / ignore audit** — `git status --short --ignored`
7. **Secret & artifact scan** — manual review plus the ignore audit above:
   confirm no `.env`, `credentials.json`, `token.json`, keys, caches, PDFs,
   or course files are tracked.
8. **File-size gate** — every Python source file stays **< 150** non-empty,
   non-comment lines: `find src tests -name "*.py" -print0 | xargs -0 wc -l`.
9. **Local MCP HTTP E2E smoke** —
   `uv run python -m mars777_cop_thief.mcp_client.smoke` must exit 0 with all
   checks true. It starts the Cop/Thief servers as local subprocesses on free
   ports, drives them over HTTP, and tears them down. Also runs as a default
   pytest integration test (`tests/integration/mcp/`); skippable with
   `RUN_MCP_E2E=0` where local subprocesses are not permitted.
10. **Local MCP-backed game smoke** —
    `uv run python -m mars777_cop_thief.mcp_client.game_smoke` must exit 0 with all
    checks true. It plays the full default game (6 sub-games) where every turn
    calls the role servers over HTTP, then tears the servers down. A one-sub-game
    variant runs as a default pytest integration test (same `RUN_MCP_E2E=0` skip).
11. **Official report validation & evidence pack** —
    `uv run python -m mars777_cop_thief.reporting.generate_evidence_pack` must
    exit 0 with `validation_status: valid` and write sanitized
    `results/evidence/*.example.json`. The internal report schema is validated and
    **token-safe** (no `auth_token`/`secret`/dummy-token keys or values); evidence
    artifacts are deterministic, token-free, and reviewable in Git.
12. **Prompted MCP game smoke (fake_local)** —
    `uv run python -m mars777_cop_thief.mcp_client.prompted_game_smoke` must exit 0
    with all checks true. It plays the full default game over HTTP where each turn
    is decided by the offline `fake_local` provider, accounting prompt/response
    tokens and cost, and tears the servers down. A one-sub-game variant runs as a
    default pytest integration test (same `RUN_MCP_E2E=0` skip).

13. **Gmail report dry-run** —
    `uv run python -m mars777_cop_thief.gmail.send_report` must exit 0 with
    `status: dry_run` and `body_json_valid: true`. It validates the official
    report and builds the JSON-only MIME message **without calling Gmail** and
    without requiring credentials/token.
14. **Hardened run smoke** —
    `uv run python -m mars777_cop_thief.run.hardened_smoke` must exit 0 with
    `status: ok` and all programmatic checks true (report_valid, totals_valid,
    no_secret_like_content, json_serializable, local_mcp_verified,
    gmail_body_json_only). It runs the fake-local full game, aggregate-validates
    the official report, and builds a secret-free run manifest.
15. **Cloud deployment preflight** —
    `uv run python -m mars777_cop_thief.deployment.preflight` must exit 0 with
    `status: ok` and all checks true (config valid, `cloud_status: not_deployed`,
    placeholder URLs, Dockerfile/.dockerignore present and covering secrets, no
    secret files, role/port resolve without a server, smoke commands documented).
    It makes **no cloud calls** and needs neither gcloud nor credentials.

### Operational cloud validation (live; env-specific)

- **Public Cloud Run smoke** —
  `COP_MCP_URL=… THIEF_MCP_URL=… COP_MCP_TOKEN=… THIEF_MCP_TOKEN=… uv run python
  scripts/public_cloud_smoke.py` must exit 0 with `passed: true`. It drives the two
  **deployed** MCP services over their public HTTPS URLs (Stage 13C): each must
  **reject a bad token** (`unauthorized`) and **accept the correct token**
  (`health_ok`, role-correct, hidden opponent not leaked, thief has no barrier
  tool). Tokens are sourced from the git-ignored `.secrets/cloud-run.local.env` and
  are **never printed**. This is an **operational** check against live cloud
  resources (not part of the offline unit gate); the underlying flow logic is the
  same `run_flow` already unit-tested offline. Live URLs/evidence:
  `results/evidence/cloud_deployment.example.json`.

- **Public-cloud full game + report dry-run** —
  `set -a; . .secrets/cloud-run.local.env; set +a; uv run python
  scripts/public_cloud_final_dry_run.py` must exit 0 with `passed: true`. It plays
  the full **6 sub-games** over the deployed public `/mcp` URLs, builds and
  **schema-validates** the official internal report (public URLs, real repo,
  `cloud_status: deployed`), and runs the Gmail sender in **dry-run only**
  (`RUN_GMAIL_LIVE` never set) → `dry_run`, `body_json_valid: true`. Tokens come from
  the git-ignored `.secrets/` and are **never printed**; evidence is token-free
  (`results/evidence/public_cloud_full_game.example.json`,
  `final_report_dry_run.example.json`). Operational (live cloud), not part of the
  offline unit gate; the game/report/validation logic is unit-tested offline.

- **Inter-group bonus readiness gate** —
  `MARS777_STUDENTS_FILE=.secrets/students.local.json uv run python
  scripts/bonus_partner_readiness.py` must exit 0 and print safe flags. It validates
  our cloud readiness, ingests the local git-ignored partner file (auto-created from
  `config/bonus_partner.template.json`), and runs a partner compatibility smoke only
  when the partner endpoints/tokens are real — otherwise `partner_smoke_passed:
  unknown` and `bonus_ready: false` with blockers. It **never** sends Gmail, runs a
  full bonus game, or prints tokens/IDs. The pure intake validation
  (`bonus/intake.py`) is in the **offline unit gate** (`tests/unit/bonus/`).

- **Partner interop adapter readiness/smoke** —
  `uv run python scripts/bonus_interop_smoke.py` must exit 0 and print safe flags. In
  readiness mode (partner URLs/tokens still pending) it reports `partner_smoke_status:
  unknown` with blockers; once the local partner file is populated the same script
  runs unauthorized + authorized + role/tool + 5x5/8x8 warm-up smokes against the
  partner endpoints — never printing secrets, never running the official bonus game.
  The pure adapter (`bonus/partner_adapter.py`) is in the **offline unit gate**
  (`tests/unit/bonus/test_partner_adapter.py`).

### Operational preflight (env-specific; not a pure unit gate)

- **Live-readiness preflight** —
  `uv run python -m mars777_cop_thief.deployment.live_readiness` must exit 0 and
  print structured JSON combining Gmail OAuth readiness, read-only cloud/`gcloud`
  readiness, and the packaging preflight, with all blockers listed. It is **read-only**:
  it never sends live Gmail and never deploys/builds/enables anything. Its *result*
  depends on the local environment (OAuth file paths, whether `gcloud` is installed/
  authenticated, billing), so it is an **operational** check, not part of the pure
  unit gate. The underlying logic is fully unit-tested with mocks/temp files
  (`tests/unit/gmail/`, `tests/unit/deployment/`) and those tests **are** in the
  default suite and make no network call. Run with the documented env vars
  (`GOOGLE_OAUTH_CLIENT_SECRETS`, `GOOGLE_OAUTH_TOKEN_PATH`, `GOOGLE_CLOUD_PROJECT`,
  `CLOUD_RUN_REGION`, `RUN_GMAIL_LIVE=0`, `RUN_CLOUD_DEPLOY=0`); real paths stay
  outside Git.

### Optional (not required for default validation)

- **Live Gmail send** —
  `RUN_GMAIL_LIVE=1 uv run python -m mars777_cop_thief.gmail.send_report` actually
  sends via the Gmail API. It is **opt-in** and requires OAuth credentials/token
  files outside the repo; normal validation never sends or needs credentials.
- **Live Gemini smoke** —
  `uv run python -m mars777_cop_thief.mcp_client.gemini_prompted_smoke` must exit 0
  in **skipped** mode (default; no key, no network). It is **opt-in** and **not
  part of default validation**: it runs a real Gemini sub-game only when
  `RUN_GEMINI_LIVE=1` and an API key are set in the local environment. Normal
  `pytest`/coverage never require a key and never call the network.
- **Live partner compatibility smoke** —
  `uv run python scripts/bonus_partner_live_smoke.py` connects to the **partner
  group's** live Cop/Thief `/mcp` endpoints and exercises the confirmed
  `setup`/`observe`/`my_move`/`state` contract (unauthorized rejected, authorized
  accepted, role identity per server, 0-based `[row,col]`, thief-first, 5x5/8x8
  warm-ups). It needs the local git-ignored `.secrets/bonus_partner.local.json`
  (partner URLs + tokens) and the partner's servers to be up, so it is **not part of
  default validation** and is skipped when those are absent. It **never** runs the
  official bonus game, sends Gmail, or prints/writes tokens; evidence is sanitized
  (`results/evidence/bonus_partner_live_smoke.example.json`). The pure verdict reducer
  **is** unit-tested in the default suite (`tests/unit/bonus/`, no network).

## Staging discipline

- **Never** run `git add .` — stage files explicitly and intentionally.
- Do not commit until changes have been reviewed and a commit is requested.

## Conventions

- Ruff is the single linter/formatter (line length 100).
- Tests must not contact external services or require credentials.
- Configuration is data (`config/*.default.json`), validated by the SDK.
