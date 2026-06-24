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
| 6 | Local MCP client & HTTP E2E smoke: subprocess server pair, FastMCP client, deterministic flow over HTTP | 🔄 |
| 7 | Natural-language protocol over MCP: message interpretation + validator + interpreted-action logs | ⏳ |
| 8 | Cop & Thief LLM agents wired through MCP | ⏳ |
| 9 | Orchestrator: run num_sub_games, seeds, aggregation, rate limits over MCP | ⏳ |
| 10 | Google report sender (Gmail/OAuth) for final results, JSON-only email body | ⏳ |
| 11 | Cloud/self-play through public, authenticated URLs | ⏳ |
| 12 | Bonus inter-group play against another group's server (mandatory scope) | ⏳ |
| 13 | Hardening: cost/measurement tracking, logging, security review | ⏳ |
| 14 | Final gap audit + submission checklist closure | ⏳ |

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

## Stage 6 checklist (current — local MCP client & HTTP E2E smoke)

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
- [ ] Reviewed and explicitly committed

### Stage 6 scope notes

- The client connects to the role servers **over HTTP** (not by importing tool
  functions) for the E2E path; direct adapter unit tests remain from Stage 5.
- Servers run as short-lived `127.0.0.1` subprocesses on free ports; tokens/ports
  are injected via the child environment (dummy local values, never committed)
  and processes are always torn down.
- **No** cloud deployment, public URLs, Gmail/email, external-LLM calls, GUI,
  production OAuth, or inter-group remote play in this stage.

## Next up (Stage 7 — natural-language protocol over MCP)

- [ ] Message interpretation + validator wired through the MCP tools
- [ ] Interpreted-action logs alongside raw NL over the transport
- [ ] Integration test exercising the tool contract without external LLM calls
