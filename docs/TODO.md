# TODO — Staged Milestones

Statuses: ✅ done · 🔄 in progress · ⏳ planned

| Stage | Milestone | Status |
|------|-----------|--------|
| 0 | Repo skeleton: package layout, docs scaffolding, config defaults, packaging, quality gates | ✅ |
| 1 | Requirements hardening & architecture planning: Requirements Matrix, acceptance criteria, risk register, inter-group protocol, plan/ADR updates | ✅ |
| 2 | Game engine: grid, 8-dir movement, barriers, capture, scoring, deterministic stepping + unit tests | ✅ |
| 3 | Local self-play pipeline: deterministic baseline policies, sub-game/full-game runners, transcripts, in-memory JSON report | ✅ |
| 4 | Local partial-observability & natural-language dialogue: visibility-radius observations, free-text messages, observed runner | ✅ |
| 5 | Local HTTP MCP servers (Cop & Thief): FastMCP, role-safe tools, token auth, run entrypoints | ✅ |
| 6 | Local MCP client & HTTP E2E smoke: subprocess server pair, FastMCP client, deterministic flow over HTTP | ✅ |
| 7 | MCP-backed local game orchestration: real sub-games/full game where each turn calls the MCP servers over HTTP | ✅ |
| 8 | Official report schema/validation + sanitized local evidence pack; bonus schema example | ✅ |
| 9 | Prompted MCP agent layer: provider interface, offline fake LLM, prompts/parser/cost, prompted game runner | ✅ |
| 10 | Optional Google Gemini provider adapter (google-genai), env config, provider factory, live-gated smoke | ✅ |
| 11 | Gmail JSON report sender: dry-run default + live-gated sending, JSON-only body, external OAuth files | ✅ |
| 12 | Hardened run validation: deterministic identity/manifest, failure classes, retry/timeout, aggregate validation | ✅ |
| 13A | Cloud deployment packaging & preflight (Dockerfile, role entrypoint, cloud config, preflight) — no live deploy | ✅ |
| 13B | Live-readiness preflight: Gmail OAuth external-file check + read-only cloud/gcloud checks + combined readiness report — no live send/deploy | ✅ |
| 13C | Live Cloud Run deployment of both MCP services (public URLs + app-level token auth) with public smoke | ✅ |
| 14A | Full public-cloud 6-sub-game flow + official report generated/validated + Gmail dry-run (no live send) | ✅ |
| 14 | Bonus inter-group play against another group's server (mandatory scope) | ⏳ |
| 15 | Hardening: cost/measurement tracking, logging, security review | ⏳ |
| 16 | Final gap audit + submission checklist closure | ⏳ |

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

## Stage 2 checklist (completed — pure game engine core)

- [x] `game/models.py` — Position, PlayerRole, ActionType, Action, ActionResult,
      RuleViolation, 8-direction deltas
- [x] `game/rules.py` — bounds, one-step movement, barrier validation predicates
- [x] `game/state.py` — `SubGameState` with turn-order-driven `current_role`
- [x] `game/engine.py` — `GameEngine.apply_action` / `score_state`, deterministic
- [x] `game/events.py` — log-ready event dicts (no file logging yet)
- [x] SDK factory `create_game_engine(path)` (entrypoint only, no game logic)
- [x] `config/game.default.json` — added explicit `turn_order` (thief first)
- [x] TDD unit tests under `tests/unit/game/` (45 tests total, 100% coverage)
- [x] Reviewed and explicitly committed

## Stage 3 checklist (completed — local self-play pipeline)

- [x] `agents/baseline.py` — deterministic Cop (toward) / Thief (away) policies
      with canonical-order fallback; `None` only when stuck
- [x] `orchestration/results.py` — `SubGameResult` + structured event/transcript
- [x] `orchestration/runner.py` — `run_sub_game` / `run_full_game`, illegal-action
      handling with legal fallback
- [x] `orchestration/totals.py` — score totals and win counts
- [x] `orchestration/report.py` — in-memory JSON-serializable report builder
      (local-only, `mcp_status: not-deployed`, not emailed)
- [x] SDK entrypoints `run_local_sub_game` / `run_local_full_game` (delegating)
- [x] `config/game.default.json` — added `github_repo` placeholder
- [x] Tests under `tests/unit/agents/` and `tests/unit/orchestration/`
      (71 tests total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 3 scope notes

- Local backbone only: **no** MCP, HTTP, agents/LLM, NL parsing, Gmail, cloud,
  GUI, or inter-group networking in this stage.
- Baseline policies are deterministic (no RNG); baseline cop does not place
  barriers. Start positions default to opposite corners each sub-game.
- A stuck actor (no legal move) ends the sub-game as a thief survival.

## Stage 4 checklist (completed — local partial-observability & dialogue)

- [x] `observability/visibility.py` — Chebyshev `is_visible` + `relative_direction`
- [x] `observability/observation.py` — `Observation` + `observe`; hidden opponent
      position is `None` (never stored)
- [x] `dialogue/messages.py` — free natural-language messages (no JSON, no coords)
- [x] `dialogue/transcript.py` — transcript records + debug-only `audit` facts
- [x] `agents/observed.py` — observation-based cop/thief policies (patrol/explore
      fallback when opponent hidden)
- [x] `orchestration/dialogue_runner.py` — observed runner recording action events
      and message transcript; Stage 3 full-state runner left intact
- [x] `orchestration/results.py` — `SubGameResult` gains optional `transcript`
- [x] `orchestration/report.py` — `mode` parameter + `visibility_radius` summary
- [x] SDK `run_local_dialogue_sub_game` / `run_local_dialogue_full_game`
- [x] Tests under `tests/unit/observability/`, `tests/unit/dialogue/`,
      `tests/unit/agents/`, `tests/unit/orchestration/` (101 tests, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 4 scope notes

- Strict separation: trusted full engine state · per-agent observation · NL
  message text · debug-only audit metadata (never consumed by the other agent).
- Observation-based policies act only on what they can see; the engine remains
  the authority and provides the runner's legal fallback (not an agent ability).
- **No** MCP, HTTP, external LLM understanding, Gmail, cloud, GUI, or inter-group
  networking in this stage; reports stay local-only and are not emailed.

## Stage 5 checklist (completed — local HTTP MCP servers)

- [x] `mcp_servers/auth.py` — env-token guard; structured unauthorized result;
      real token never logged/returned (`REDACTED`)
- [x] `mcp_servers/common.py` — JSON↔domain helpers, HTTP settings reader
- [x] `mcp_servers/tools.py` — pure role-safe adapters (role info, health,
      observation, message, propose_action, barrier_candidate)
- [x] `mcp_servers/cop_server.py` / `thief_server.py` — FastMCP builders;
      thief omits barrier placement
- [x] `mcp_servers/run_cop.py` / `run_thief.py` — HTTP entrypoints (`main()` only
      starts a server; import is side-effect free)
- [x] `config/mcp.local.default.json` — transport/ports/paths/token-env/local_only
- [x] `.env-example` — `COP_MCP_TOKEN`/`THIEF_MCP_TOKEN`/`*_MCP_LOCAL_URL` placeholders
- [x] FastMCP added via uv and pinned (`fastmcp>=3.4.2,<4`; uv.lock pins exact)
- [x] Tests under `tests/unit/mcp_servers/` (127 tests total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 5 scope notes

- The LLM lives in the future client, **not** in the MCP servers; servers only
  expose tools that delegate to the domain packages (engine stays authoritative).
- HTTP transport from the start (FastMCP `transport="http"`); two independent
  servers on separate local ports (Cop 8001, Thief 8002).
- Stage 5 auth is an explicit `auth_token` argument checked against an env var —
  **local development auth**, to be upgraded for cloud.
- **No** cloud deployment, public URLs, Gmail/email, external-LLM calls, GUI,
  production OAuth, or inter-group remote play in this stage.

## Stage 6 checklist (completed — local MCP client & HTTP E2E smoke)

- [x] `mcp_client/client.py` — FastMCP client URL helpers + bounded `wait_ready`
- [x] `mcp_client/subprocess_pair.py` — free ports, env-token/port injection,
      `server_pair` context manager that always terminates (escalates to kill)
- [x] `mcp_client/e2e_flow.py` — deterministic flow (health, role info, auth ±,
      hidden-state, message, action, thief-no-barrier) → JSON-serializable result
- [x] `mcp_client/smoke.py` — `run_smoke()` + `main()`; exits 0 only on pass
- [x] `mcp_servers/common.py` `resolve_port` + run entrypoints honor `*_MCP_PORT`
- [x] Real HTTP E2E integration test (`tests/integration/mcp/`, default-on,
      skippable via `RUN_MCP_E2E=0`) plus in-memory flow tests for coverage
- [x] Smoke verified passing over real HTTP: `uv run python -m
      mars777_cop_thief.mcp_client.smoke` → exit 0, all checks true
- [x] Tests (143 total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 6 scope notes

- The client connects to the role servers **over HTTP** (not by importing tool
  functions) for the E2E path; direct adapter unit tests remain from Stage 5.
- Servers run as short-lived `127.0.0.1` subprocesses on free ports; tokens/ports
  are injected via the child environment (dummy local values, never committed)
  and processes are always torn down.
- **No** cloud deployment, public URLs, Gmail/email, external-LLM calls, GUI,
  production OAuth, or inter-group remote play in this stage.

## Stage 7 checklist (completed — MCP-backed local game orchestration)

- [x] `mcp_client/game_flow.py` — `run_mcp_sub_game`/`run_mcp_full_game`: each
      turn calls `get_observation`→`compose_message`→`propose_action` over the
      client; engine applies the action; illegal proposal → recorded + legal fallback
- [x] `mcp_client/game_report.py` — `build_mcp_report` with local status fields
      (`transport`, `mcp_status`, urls, `cloud_status`, `email_status`,
      `hidden_state_respected`); JSON-serializable; no tokens stored
- [x] `mcp_client/game_smoke.py` — `run_game_smoke()` + `main()`; full default
      game over HTTP; exits 0 only on pass; always tears servers down
- [x] SDK `run_local_mcp_sub_game` / `run_local_mcp_full_game` (delegating)
- [x] Real-HTTP one-sub-game integration test (default-on, `RUN_MCP_E2E=0` skips)
      + in-memory full-game/flow/report unit tests
- [x] Full 6-sub-game game smoke verified passing over real HTTP: `uv run python
      -m mars777_cop_thief.mcp_client.game_smoke` → exit 0, all checks true
- [x] Tests (160 total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 7 scope notes

- The trusted orchestrator owns authoritative state; the **engine** stays the only
  authority for legality/capture/scoring. Each turn calls the role's MCP tools
  **over HTTP** (in-memory client only in unit tests).
- The orchestrator may send full state to `get_observation`, but the server
  returns only the role-safe filtered observation and `propose_action` consumes
  only that; transcripts carry no hidden coordinates (`hidden_state_respected`).
- Dummy local tokens are injected via the child env at runtime; reports never
  contain tokens. **No** cloud/public URLs, Gmail/email, external-LLM, GUI,
  production OAuth, or inter-group remote play in this stage.

## Stage 8 checklist (completed — official report schema, validation & evidence)

- [x] `reporting/schemas.py` — internal/bonus required-field sets, forbidden
      token patterns, normalized evidence placeholders
- [x] `reporting/validators.py` — `validate_internal_report`/`validate_bonus_report`,
      recursive `find_token_like`, local-URL-only-when-local rule
- [x] `reporting/official_report.py` — `build_official_internal_report` (validated)
      + `build_bonus_report_example` (no real run claimed)
- [x] `reporting/evidence.py` — sanitized writer (normalized URLs/timestamp,
      summary, short transcript excerpt; refuses unsanitized input)
- [x] `reporting/generate_evidence_pack.py` — CLI; validates and writes the pack
- [x] SDK `validate_internal_report` / `build_official_internal_report` /
      `generate_local_evidence_pack` (delegating)
- [x] `.gitignore` tracks only `results/evidence/*.example.json`
- [x] Committed deterministic evidence artifacts (report/summary/transcript excerpt)
- [x] Evidence command verified: `uv run python -m
      mars777_cop_thief.reporting.generate_evidence_pack` → valid, exit 0
- [x] Tests (189 total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 8 scope notes

- Reports are JSON-only (email-body ready) and **token-safe** — validation rejects
  token-like keys/values and dummy tokens; reports omit all tokens.
- Evidence is **deterministic** (the game is deterministic; URLs/timestamp are
  normalized to placeholders) and **small** (no full event logs, ≤4-message
  excerpt) so it is reviewable in Git.
- The **bonus schema is an example only** — `bonus_claim: false`,
  `mutual_agreement: false`; **no real inter-group game has been run**.
- **No** Gmail/email sending, cloud deployment, public URLs, external-LLM, GUI,
  production OAuth, or real inter-group remote play in this stage.

## Stage 9 checklist (completed — prompted MCP agent layer)

- [x] `llm/provider.py` — provider Protocol + `LlmResponse` (token/cost fields)
- [x] `llm/fake_provider.py` — deterministic offline `fake_local` provider
      (reasons over the role-safe observation; never emits opponent coordinates)
- [x] `llm/prompts.py` — role prompts (qualitative opponent direction only; no
      hidden coordinates, no tokens/secrets)
- [x] `llm/parser.py` — `ACTION:` parser (8 directions, hyphen/underscore; cop
      barrier; rejects stay/malformed)
- [x] `llm/cost.py` — non-negative token/cost estimator (fake rate = 0)
- [x] `llm/agent.py` — `LlmAgent.decide` → structured decision with parse status
- [x] `mcp_client/prompted_game_flow.py` — per-turn observation→prompt→provider→
      parse→engine; records prompt summary, response, parse status, tokens, cost,
      fallback_used; deterministic fallback on bad/illegal actions
- [x] `mcp_client/game_report.py` `build_prompted_report` — `llm_mode`/provider/
      token/cost/parse_failures/fallbacks_used fields
- [x] `mcp_client/prompted_game_smoke.py` + SDK `run_local_prompted_mcp_game`
- [x] Full 6-sub-game prompted game verified over real HTTP: `uv run python -m
      mars777_cop_thief.mcp_client.prompted_game_smoke` → exit 0, all checks true
      (24,762 prompt + 2,574 response tokens, cost 0.0, 0 parse failures/fallbacks)
- [x] Tests under `tests/unit/llm/` + prompted flow/integration (229 total, 100%)
- [x] Reviewed and explicitly committed

### Stage 9 scope notes

- The provider lives on the orchestrator side, **never in the MCP servers**; the
  engine stays the only authority. The agent receives only the role-safe
  observation + message + rules + allowed actions — never hidden coordinates.
- Output is natural-language with an `ACTION:` line; a safe parser extracts the
  action and the orchestrator falls back deterministically on parse/legality
  failure (recorded as `parse_failures`/`fallbacks_used`).
- **No** real external LLM API, API keys, cloud, public URLs, Gmail, GUI, or real
  inter-group remote play — only the offline `fake_local` provider.

## Stage 10 checklist (completed — optional Gemini provider, live-gated)

- [x] `google-genai` added via uv and pinned (`google-genai>=2.10.0`; uv.lock exact)
- [x] `config/llm.default.json` — provider/allowed_providers/env-var names/defaults
      (no keys); `.env-example` Gemini placeholders only
- [x] `llm/config.py` — load LLM config + `LlmConfigError`
- [x] `llm/gemini_provider.py` — `GeminiProvider` over `google-genai`
      (`generate_content`, no streaming/tools); actual usage tokens when present,
      else estimator; key held privately, never logged/returned/in metadata
- [x] `llm/provider_factory.py` — `create_provider_from_env` (default fake_local;
      gemini only when requested + key present; controlled error otherwise);
      no import-time API calls
- [x] `mcp_client/gemini_prompted_smoke.py` — live-gated; skips (exit 0) unless
      `RUN_GEMINI_LIVE=1`; controlled failure if enabled without a key; one short
      bounded sub-game when enabled with a key; never prints the key
- [x] Mocked unit tests (no network): factory, provider mapping/malformed/secrets,
      smoke gate (245 total, 100% coverage)
- [x] Live Gemini smoke **skipped by design** (no key, `RUN_GEMINI_LIVE` unset):
      `uv run python -m mars777_cop_thief.mcp_client.gemini_prompted_smoke` → exit 0
- [x] Reviewed and explicitly committed

### Stage 10 scope notes

- Gemini is **opt-in**; `fake_local` remains the default and the deterministic,
  grading-safe mode. Normal tests/validation require **no API key**.
- The key is read from the environment only and is **never logged, returned, or
  put in metadata**. The provider lives on the orchestrator side, never in the
  servers; hidden coordinates are never sent in prompts.
- **No** committed/required API key, cloud deployment, public URLs, Gmail/email,
  GUI, or real inter-group remote play. The live Gemini smoke was **not run**
  here (no key); it is available behind `RUN_GEMINI_LIVE=1`.

## Stage 11 checklist (completed — Gmail JSON report sender)

- [x] `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
      added via uv and pinned (uv.lock exact)
- [x] `config/gmail.default.json` — recipient/subject/scope/env-var names/gates
      (no secrets); `.env-example` Gmail placeholders + dry-run defaults
- [x] `gmail/config.py` — load + validate config; resolve recipient/paths from env
      (never requires OAuth files at import/load)
- [x] `gmail/mime_builder.py` — JSON-only body (`json.dumps(...)`), base64url raw
      message; decode/parse-back helpers (no greeting/signature)
- [x] `gmail/auth.py` — lazy credential load/refresh/flow with injected deps;
      controlled `GmailAuthError`; OAuth flow only when `RUN_GMAIL_AUTH=1`;
      never logs secret content
- [x] `gmail/sender.py` — `DryRunGmailSender` (no API call) + `GmailApiSender`
      (mockable service); `SendResult` (no secrets, JSON-serializable)
- [x] `gmail/send_report.py` — CLI: dry-run unless `RUN_GMAIL_LIVE=1`; controlled
      failure (exit non-zero) when live without credentials; JSON result only
- [x] SDK `build_gmail_report_message` / `dry_run_gmail_report` /
      `validate_gmail_message_body`
- [x] Mocked unit tests, no live calls (271 total, 100% coverage); body parses
      back to the report object (JSON-only proven)
- [x] Dry-run verified: `uv run python -m mars777_cop_thief.gmail.send_report` →
      `status: dry_run`, `body_json_valid: true`, exit 0
- [x] Reviewed and explicitly committed

### Stage 11 scope notes

- Email **body is JSON only** — exactly `json.dumps(report, ensure_ascii=False,
  indent=2)`; subject is human-readable. No tokens/secrets in body, headers,
  logs, result, or report.
- Live sending is **opt-in** (`RUN_GMAIL_LIVE=1`) with the minimal `gmail.send`
  scope and OAuth files **outside the repo**; a **live email was not sent** here.
- **No** `credentials.json`/`token.json`/`.env` committed, cloud deployment,
  public URLs, GUI, or real inter-group remote play.

## Stage 12 checklist (completed — hardened run validation)

- [x] `run/identity.py` — deterministic `run_id` (group/stage/config-hash/seed);
      injectable timestamp + git commit; config fingerprint; no secrets
- [x] `run/manifest.py` — JSON manifest (capabilities enabled/disabled, gates,
      scan status); `scan_manifest_secrets` exempts the scan-status meta keys
- [x] `run/status.py` — 12 failure categories + exception classifier + redaction
- [x] `run/retry.py` + `config/runtime.default.json` — validated `RetryPolicy`
      and injectable `retry_call` (fast, bounded); `run/rate_limit.py` resource guard
- [x] `run/validation.py` — aggregate `validate_full_report` (count/totals/winners/
      outcomes/status-fields/token-scan/url-locality + manifest cloud cross-check)
- [x] `run/hardened_smoke.py` — full prompted run → official report → aggregate
      validation → manifest → programmatic gates; JSON summary, no secrets/raw logs
- [x] SDK `build_run_manifest` / `validate_full_report` / `run_hardened_local_smoke`
- [x] Hardened smoke verified: `uv run python -m mars777_cop_thief.run.hardened_smoke`
      → `status: ok`, all checks true, exit 0 (totals cop 30 / thief 60)
- [x] Tests under `tests/unit/run/` (302 total, 100% coverage)
- [x] Reviewed and explicitly committed

### Stage 12 scope notes

- Same config + seed → same `run_id` and stable config hash (timestamp/git are
  injectable for deterministic tests).
- Failures are **classified**, not hidden; manifests/results carry **no secrets**
  (the scan exempts only the scan-status meta field names, not content).
- **No** cloud deployment, public URLs, live Gmail send, GUI, or real inter-group
  remote play; live Gemini runs only behind the existing `RUN_GEMINI_LIVE` gate.

## Stage 13A checklist (current — cloud deployment packaging & preflight)

- [x] `Dockerfile` — single role-aware image (uv, locked deps, src/config only);
      no secrets baked; `MCP_ROLE` selects cop/thief at runtime
- [x] `.dockerignore` — excludes `.git`, `.venv`, `.env`, credentials/token, caches,
      tests, results, keys, and course documents
- [x] `mcp_servers/cloud_entrypoint.py` — `MCP_ROLE`/`PORT`/`0.0.0.0` resolution,
      role-token check (name only, never the value), controlled error + exit 1
- [x] `config/cloud.default.json` — target Cloud Run, service placeholders, env-var
      names, `<set-after-deployment>` URLs, `cloud_status: not_deployed`
- [x] `deployment/` — `cloud_config.py`, `docker_checks.py`, `preflight.py`
- [x] `scripts/cloud_run_deploy_template.sh` — inert template (gated by
      `RUN_CLOUD_DEPLOY=1`); placeholders only; not run in validation
- [x] `docs/CLOUD_DEPLOYMENT.md` — future deploy/rollback/revoke guide (placeholders)
- [x] `.env-example` — `MCP_ROLE`/`PORT`/`*_PUBLIC_URL`/`RUN_CLOUD_DEPLOY` placeholders
- [x] Preflight verified: `uv run python -m mars777_cop_thief.deployment.preflight`
      → `status: ok`, all checks true, exit 0
- [x] Tests under `tests/unit/deployment/` (321 total, 100% coverage)
- [ ] Reviewed and explicitly committed

### Stage 13A scope notes

- **No live deployment was performed**; **no Cloud Run service was created**;
  **no public URL exists** (placeholders only, `cloud_status: not_deployed`).
- Tokens come from the runtime env / secret manager — never image build args,
  `Dockerfile ENV`, logs, docs examples, or committed files; the entrypoint never
  prints a token value.
- Local mode still binds `127.0.0.1`; cloud mode binds `0.0.0.0` and reads `PORT`.

## Stage 13B — live-readiness preflight (this stage)

- [x] `gmail/preflight.py` — external OAuth file readiness (paths only; no content
      read); returns `status`/`credentials_file_exists`/`token_file_exists`/
      `outside_repo`/`live_send_enabled`/`blockers`/`warnings`
- [x] `deployment/gcloud_checks.py` — read-only gcloud checks (install, active
      account presence, active project vs `api-mars-777`, region, best-effort
      billing); missing/blocked states never crash
- [x] `deployment/live_readiness.py` — combined Gmail + cloud + packaging report;
      `uv run python -m mars777_cop_thief.deployment.live_readiness` exits 0 with
      blockers listed; sends no live Gmail, deploys nothing
- [x] Tests under `tests/unit/gmail/` + `tests/unit/deployment/` (340 total, 100%)
- [x] Manual OAuth smoke succeeded externally (Gmail draft + Calendar event);
      OAuth files stay outside the repo and are never committed/printed
- [ ] Reviewed and explicitly committed

### Stage 13B scope notes

- **No live Gmail send and no cloud deployment were performed.** The preflight is
  read-only: existence/location and read-only `gcloud` state only.
- Known blockers on this machine: `gcloud` not installed (so account/project/
  billing are unknown). Gmail OAuth files are present outside the repo.
- Expected project `api-mars-777`; recommended region `me-west1`. Real absolute
  OAuth paths are used only at command runtime, never committed to config/docs.

## Stage 13C — live Cloud Run deployment (this stage)

- [x] Deployed `mars777-cop-mcp` and `mars777-thief-mcp` to Cloud Run
      (`api-mars-777` / `me-west1`) from the repo `Dockerfile` via `--source .`
- [x] Per-service tokens generated locally with Python `secrets`, stored only in
      git-ignored `.secrets/`; supplied via `--env-vars-file` (never on cmdline)
- [x] IAM public + **app-level token auth**; raw `GET /`→404, `GET /mcp`→406
- [x] Public smoke passed (`scripts/public_cloud_smoke.py`): both services reject a
      bad token and accept the correct one; role-correct; no hidden-state leak
- [x] Sanitized evidence (no tokens): `results/evidence/cloud_deployment.example.json`
- [x] APIs enabled (only required): run, cloudbuild, artifactregistry
- [ ] Reviewed and explicitly committed

### Stage 13C scope notes

- **No live Gmail send, no final official report, and no inter-group bonus run**
  were performed. Final submission is **not** complete.
- `config/cloud.default.json` stays the not-yet-deployed packaging template so the
  packaging preflight remains a valid pre-deploy gate; live state is in the
  evidence file. No token value is in any tracked file.

## Stage 14A — public-cloud full game + final report dry-run (this stage)

- [x] Played the full 6 sub-games over the public `/mcp` URLs
      (`scripts/public_cloud_final_dry_run.py`); 6/6 decided, totals cop 30/thief 60
- [x] Built + schema-validated the official internal report (group MaRs-777,
      students, real `github_repo`, public `cop_mcp_url`/`thief_mcp_url`, timezone,
      `sub_games`, `totals`, `cloud_status: deployed`) → `validation_status: valid`
- [x] Gmail sender **dry-run only** with that report → `dry_run`, `body_json_valid`
- [x] Token-free evidence: `results/evidence/public_cloud_full_game.example.json`,
      `results/evidence/final_report_dry_run.example.json`
- [x] Tokens stayed only in git-ignored `.secrets/`; never printed/committed
- [ ] Reviewed and explicitly committed

### Stage 14A scope notes

- **No live Gmail send** (`RUN_GMAIL_LIVE` never set to 1), **no inter-group bonus
  run**, and the final submission is **not** complete. The live email and bonus
  match are the only items left.

### Stage 14B — student-ID privacy hotfix

- [x] Real student national-IDs **removed from every tracked file** (script +
      evidence); no ID literals remain in source.
- [x] Real identities live only in a local **git-ignored** file
      (`MARS777_STUDENTS_FILE`, default `.secrets/students.local.json`); the script
      loads them at runtime for the in-memory report + Gmail dry-run.
- [x] Tracked evidence **redacts** the IDs (`id: REDACTED`) and adds the
      `identity_privacy` flags; English/Hebrew names retained.
- [x] Committed and pushed.

### Stage 14B — public-history scrub

- [x] Approved one-time `git filter-repo` rewrite (national-IDs → `REDACTED_STUDENT_ID`)
      + `git push --force-with-lease`; private pre-scrub backup taken outside the repo.
- [x] **All reachable history is ID-free** — verified locally and in a fresh clone
      (0 matches). Repo stayed public. GitHub internal-cache caveat documented.

### Stage 14C — Gmail draft preview (no send)

- [x] Created a Gmail **draft** (not sent) of the official Assignment 6 JSON report,
      addressed to the **authenticated self account** (not the lecturer); subject
      `PREVIEW ONLY - MaRs-777 Assignment 6 JSON Report`.
- [x] Body is the JSON-only official report (real IDs loaded from the local ignored
      file in memory); `body_json_valid` + `report_schema_valid`, no placeholders.
- [x] Sanitized evidence `results/evidence/gmail_draft_preview.example.json`
      (flags only; no IDs, no body, `live_gmail_sent: false`).
- [ ] Reviewed and explicitly committed

### Stage 15A — inter-group bonus readiness gate (prepared, not completed)

- [x] Readiness gate `scripts/bonus_partner_readiness.py` + tested pure intake module
      (`src/mars777_cop_thief/bonus/intake.py`, `tests/unit/bonus/`).
- [x] Self checks pass: our public `/mcp` URLs, local Cloud Run tokens, local student
      identities, and Gmail OAuth are all ready (`self_cloud_ready: true`).
- [x] Partner intake is a **local git-ignored** file
      (`.secrets/bonus_partner.local.json`, auto-created from the tracked
      `config/bonus_partner.template.json`); tokens stay local, never committed.
- [x] Strategy recorded (`config/bonus_strategy.default.json`): pairing, scoring,
      turn-order caveat, safe defaults — no guaranteed-victory claim.
- [x] Sanitized evidence `results/evidence/bonus_readiness.example.json`
      (`bonus_ready: false`, no tokens, no IDs) with explicit blockers.
- [ ] **Pending (Stage 15B):** fill the local partner file, pass the partner
      compatibility smoke, and run the real bonus game.

> Bonus readiness is **prepared, not completed** — no real partner smoke has passed
> and no bonus game has been run. The Stage 14C draft remains a student-only preview,
> not the official submission.

### Stage 15B — partner interop adapter prep (adapter ready; game not run)

- [x] Adapter for partner group **orcai-mj**'s `setup`/`observe`/`my_move`/`state`
      contract: pure module `src/mars777_cop_thief/bonus/partner_adapter.py`
      (0-based `[row, col]`, thief-first, ≤25 moves, ≤5 cop barriers) + tests
      (`tests/unit/bonus/test_partner_adapter.py`).
- [x] Configurable board size **5x5 and 8x8** supported; official size **not frozen**.
- [x] Our existing MCP interface unchanged; our engine already 0-based `[row, col]`.
- [x] Readiness/smoke script `scripts/bonus_interop_smoke.py`: readiness mode now
      (partner URLs/tokens pending), and the same script runs unauthorized +
      authorized + role/tool + 5x5/8x8 warm-up smokes once the local partner file
      is populated — never printing secrets.
- [x] Sanitized evidence `results/evidence/bonus_interop_readiness.example.json`.
- [x] **Resolved in Stage 15C:** tool arg schemas confirmed against the live
      endpoints; the adapter was reconciled to the real contract (see below).

> The partner repo `akariya-mohammed/orcai-mj-hw6` / its INTEROP doc could not be
> fetched (404 / not public yet), so the Stage 15B adapter payload keys were
> **provisional** and had to be confirmed on the live endpoints (done in 15C).

### Stage 15C — live partner compatibility smoke + adapter reconciliation (this stage)

- [x] Both partner endpoints reachable (Cloudflare tunnel `/mcp` URLs from the local
      git-ignored partner file); tokens present. **No tokens printed or committed.**
- [x] Confirmed the partner's **real** contract live (their INTEROP doc was still not
      public) and **reconciled the adapter** — the Stage 15B provisional keys were
      wrong on every payload:
  - token key is `token` (not `auth_token`); a missing/invalid token is rejected.
  - `setup(cop, thief, rows, cols, origin, max_moves, max_barriers, diagonal, token)`
    — `cop`/`thief` are 0-based `[row,col]` **start positions** (required);
    `origin` is an integer (`0`); `diagonal` is a bool. Returns `{role, snapshot}`.
  - `observe(message, mover, token)` — opponent-move notification (destination
    parsed from `message`); `my_move(token)` — the partner picks **its own** move
    (no move arg); `state(token)` — snapshot.
- [x] Adapter rewritten (`bonus/partner_adapter.py`) + tests updated for the discovered
      contract (`test_partner_adapter.py`); pure verdict reducer tested
      (`test_partner_live_smoke_verdict.py`). 100% coverage retained.
- [x] New live smoke `scripts/bonus_partner_live_smoke.py`: unauthorized rejected,
      authorized accepted, setup/observe/my_move/state OK, **role identity** consistent
      per server (cop→`cop`, thief→`thief`), 0-based `[row,col]` accepted, **thief-first**
      accepted, **5x5 and 8x8** warm-ups both pass → `partner_smoke_passed: true`.
- [x] `bonus_interop_smoke.py` `_live` + `bonus_partner_readiness.py` `_partner_smoke`
      updated to the confirmed contract; both now report `partner_smoke_status/passed:
      passed` against the live endpoints.
- [x] Sanitized evidence `results/evidence/bonus_partner_live_smoke.example.json`
      (`partner_smoke_run: true`, `partner_smoke_passed: true`,
      `official_board_size_recommendation: 5x5`, `official_bonus_game_run: false`,
      `live_gmail_sent: false`, `tokens_recorded: false`).
- [x] Official board size **recommendation: 5x5** (our baseline; both 5x5/8x8 work) —
      **not frozen** here; mutual agreement still pending.
- [ ] **Still pending:** freeze board size by mutual written agreement; play the real
      6-sub-game match; send the final live report. **No official bonus game was run.**

> Stage 15C is **compatibility only** — the official 6-sub-game bonus game was **not**
> run, no Gmail was sent, and no tokens/IDs were printed or committed.

### Stage 15D — official inter-group bonus game run + canonical bonus_game JSON (this stage)

- [x] Partner **confirmed the official rules in writing**: 8x8, 6 sub-games, ≤25 moves,
      ≤5 cop-only barriers, diagonal, thief-first, 0-based `[row, col]`, assignment scoring.
- [x] Automated cross-group **referee** (`src/.../bonus/referee.py` + `sessions.py` +
      `cross_engine.py`): our `GameEngine` is the single canonical authority (8x8,
      thief-first, ≤25 plies, ≤5 cop barriers). One role is our deployed Cloud Run MCP
      (our contract), the other the partner's MCP (orcai-mj `setup`/`observe`/`my_move`/
      `state`). **A human chooses no moves.** Our moves are mirrored to the partner via
      `observe`; the partner's own moves come from `my_move`.
- [x] **Both directions played** (the orchestration supports both — not stopped/faked):
      Set A (3) MaRs-777 Cop vs orcai-mj Thief; Set B (3) orcai-mj Cop vs MaRs-777 Thief.
- [x] Result (deterministic; `scripts/run_bonus_game.py`): **6/6 sub-games decided, 8x8**.
      Set A → orcai-mj thief survived 25 moves ×3; Set B → orcai-mj cop captured at move
      14 ×3. **totals_by_group: MaRs-777 30, orcai-mj 90 (orcai-mj 6 wins / 0)**.
      `result_hash a0fdf72d…72ac68`; `validation_status: valid`.
- [x] **Honest limitation noted:** our deployed servers were provisioned for the 5x5
      visibility config, so on the 8x8 board our agents play weaker (patrol stays near the
      5x5 centre; far-edge moves defer to the engine's documented legal fallback). The
      partner's agents were stronger. This is the real, autonomous outcome — not faked.
- [x] Canonical `bonus_game` JSON + token-free partner handoff (with `result_hash`) +
      sanitized run evidence written; **all student national IDs redacted** (both groups).
- [x] `mutual_agreement: false`, `partner_confirmation_status: pending` — set only after
      the partner confirms the canonical result matches. **No Gmail sent; bonus report not
      sent.**

> Stage 15D **ran the official bonus game** (6/6, both directions, autonomously) and
> produced the canonical `bonus_game` JSON + handoff. It did **not** send Gmail, did
> **not** send the bonus report, and did **not** set mutual_agreement (partner
> confirmation pending). No tokens or student IDs were printed or committed.

## Next up (Stage 15E+ — partner confirmation + final live report)

- [x] Receive partner `/mcp` URLs + tokens; fill `.secrets/bonus_partner.local.json` (15C)
- [x] Pass the live partner compatibility smoke (unauthorized + authorized + warm-ups) (15C)
- [x] Freeze official board size (8x8) by mutual written agreement (15D)
- [x] Play the real inter-group match (6 sub-games) and produce a `bonus_game` report (15D)
- [ ] Send the partner the handoff; once both `result_hash`es match, set
      `mutual_agreement: true` / `partner_confirmation_status: confirmed`
- [ ] Send the final official report **to the lecturer** via Gmail
      (`RUN_GMAIL_LIVE=1`, external OAuth) — still pending
- [ ] Close `FINAL_GAP_AUDIT.md` and the submission checklist (students already real)
