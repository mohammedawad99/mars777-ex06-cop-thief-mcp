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

## Stage 2 — Pure game engine core (2026-06-23)

**Goal:** Implement the pure, deterministic, config-driven Cop-and-Thief game
engine with TDD. Domain logic only — **no** MCP servers, HTTP, agents/LLM,
natural-language parsing, Gmail/Google API, cloud, GUI, or bonus networking.

**Key constraints captured from the prompt:**
- Zero-based `(row, col)` coordinates; rectangular board (default 5×5 from config).
- Eight-direction one-step movement; no stay in baseline.
- Turn-based, **thief first then cop** by default (read from config `turn_order`).
- Thief moves only; cop may move or place a barrier (≤ 5 per sub-game).
- Barriers block both players and cannot sit out of bounds, on a player, or on an
  existing barrier; moving out of bounds, into a barrier, more than one step, or
  staying is illegal.
- Capture when cop and thief share a cell after a legal move (either direction);
  thief wins at `max_moves` without capture; scoring from config.
- Illegal actions return a structured `ActionResult` (never crash); engine emits
  log-ready event dicts but does no file logging yet.
- No new external dependencies (standard library only); every source file under
  150 non-empty/non-comment lines; coverage ≥ 85.

**Artifacts produced:**
- `src/mars777_cop_thief/game/` — `models.py`, `rules.py`, `state.py`,
  `engine.py`, `events.py`, `__init__.py`.
- SDK factory `AssignmentSdk.create_game_engine(path)` (entrypoint only).
- `config/game.default.json` — added explicit `turn_order`.
- `tests/unit/game/` — `test_models.py`, `test_rules.py`, `test_engine.py`,
  `test_events.py`, `test_sdk_engine.py`, `conftest.py` (45 tests, 100% coverage).
- Doc updates: `TODO.md`, `DECISIONS.md` (ADR-0012…ADR-0014),
  `REQUIREMENTS_MATRIX.md`, `ACCEPTANCE_CRITERIA.md`, `README.md`.

**Outcome:** Pure game engine core implemented; all quality gates pass (ruff
clean, 45 tests, 100% coverage). No MCP/Gmail/LLM/cloud/bonus implementation.

## Stage 3 — Local self-play pipeline (2026-06-24)

**Goal:** Implement a local autonomous self-play pipeline on top of the Stage 2
pure engine, as the deterministic backbone later MCP agents and natural-language
orchestration will call or mirror. **No** MCP, HTTP, cloud, Gmail/Google, LLM,
natural-language parsing, GUI, or inter-group networking.

**Key constraints captured from the prompt:**
- Deterministic baseline policies: cop steps toward the thief, thief steps away
  from the cop; structured `Action` objects only; no external calls; first legal
  fallback from a fixed canonical ordering; no randomness.
- Sub-game runner: thief-first turn order via the engine, stops on capture or
  `max_moves`, returns a structured `SubGameResult` (winner, scores, final
  positions, move count, barriers, events); illegal policy actions recorded and
  safely replaced by a legal fallback.
- Full-game runner over `num_sub_games` (default 6); sanity sizes 2×2…5×5;
  JSON-serializable in-memory report (group code/slug, github_repo placeholder,
  timezone, config summary, sub_games, totals). Report is **not** emailed.
- Structured (not free-text) events with actor, turn index, action type,
  legal/illegal result, positions before/after, capture/winner.
- No overclaiming cloud/MCP/Gmail readiness (`mcp_status: not-deployed`).
- Standard library only; every file < 150 non-empty/non-comment lines; ≥ 85
  coverage.

**Artifacts produced:**
- `src/mars777_cop_thief/agents/` — `baseline.py`, `__init__.py`.
- `src/mars777_cop_thief/orchestration/` — `results.py`, `runner.py`,
  `totals.py`, `report.py`, `__init__.py`.
- SDK entrypoints `run_local_sub_game` / `run_local_full_game` (delegating).
- `config/game.default.json` — added `github_repo` placeholder.
- `tests/unit/agents/` and `tests/unit/orchestration/` plus a shared
  `tests/unit/conftest.py` (71 tests total, 100% coverage).
- Doc updates: `README.md`, `TODO.md`, `DECISIONS.md` (ADR-0015/ADR-0016),
  `REQUIREMENTS_MATRIX.md`, `ACCEPTANCE_CRITERIA.md`, `PLAN.md`.

**Outcome:** Local deterministic self-play pipeline implemented; all quality
gates pass (ruff clean, 71 tests, 100% coverage). No MCP/Gmail/LLM/cloud/bonus
implementation added.

## Stage 4 — Local partial-observability & dialogue layer (2026-06-24)

**Goal:** Add a local partial-observability and free natural-language dialogue
layer on top of the Stage 3 self-play backbone. **No** MCP, HTTP endpoints,
cloud, Gmail/Google, external-LLM understanding, GUI, or inter-group networking.

**Key constraints captured from the prompt:**
- Strict separation of four concerns: trusted full engine state · per-agent
  observation · natural-language message text · debug-only audit metadata.
- Partial observability via `visibility_radius` (default 1) and Chebyshev
  distance; an agent always knows its own role/position, board size, move
  counts, locally visible barriers, and (cop) its barrier budget; the opponent's
  position is known **only when within the radius**, otherwise `None` — the
  hidden coordinate is never stored or leaked (proven by tests).
- Free natural-language messages (not JSON, not a numeric protocol); qualitative
  relative-direction language when visible; no exact coordinates; "cannot see"
  message when hidden. Transcript records carry sender, recipient, turn index,
  message text, visibility flag, and audit facts used for evidence only — never
  consumed by the other agent.
- Observation-based policies decide from the observation only (cop toward visible
  thief, else patrol toward centre; thief away from visible cop, else explore
  toward edges); tests prove no hidden-state cheating. The engine stays
  authoritative and provides the runner's legal fallback.
- Stage 3 full-state runner preserved; standard library only; every file < 150
  non-empty/non-comment lines; ≥ 85 coverage.

**Artifacts produced:**
- `src/mars777_cop_thief/observability/` — `visibility.py`, `observation.py`,
  `__init__.py`.
- `src/mars777_cop_thief/dialogue/` — `messages.py`, `transcript.py`,
  `__init__.py`.
- `src/mars777_cop_thief/agents/observed.py` + `agents/__init__.py` exports.
- `src/mars777_cop_thief/orchestration/dialogue_runner.py`; `results.py`
  (`transcript` field), `report.py` (`mode` + `visibility_radius`),
  `__init__.py` exports.
- SDK `run_local_dialogue_sub_game` / `run_local_dialogue_full_game`.
- Tests under `tests/unit/observability/`, `tests/unit/dialogue/`, plus new
  `tests/unit/agents/test_observed.py` and dialogue runner/SDK tests
  (101 tests total, 100% coverage).
- Doc updates: `README.md`, `TODO.md`, `DECISIONS.md` (ADR-0017…ADR-0019),
  `REQUIREMENTS_MATRIX.md`, `ACCEPTANCE_CRITERIA.md`, `PLAN.md`.

**Outcome:** Local partial-observability and natural-language dialogue layer
implemented; all quality gates pass (ruff clean, 101 tests, 100% coverage). No
MCP/HTTP/Gmail/external-LLM/cloud/inter-group implementation added.

## Stage 5 — Local HTTP MCP servers (2026-06-24)

**Goal:** Implement two local HTTP-based MCP servers (Cop and Thief) that expose
role-safe tools delegating to the existing engine / observability / dialogue /
policy code. **No** cloud deployment, public URLs, Gmail, external-LLM calls,
GUI, production OAuth, or inter-group remote play.

**Key constraints captured from the prompt:**
- The LLM does **not** live in the MCP server; servers expose tools/resources for
  a future client/orchestrator. Game logic stays in the domain packages; MCP
  modules only delegate.
- Two independent server entrypoints (Cop, Thief) over **HTTP** transport,
  runnable on separate local ports.
- Tools: `get_role_info`, `get_observation` (role-safe, hidden opponent never
  leaked), `compose_message` (free text), `propose_action` (observation-based
  policy), `health_check`; cop-only `place_barrier_candidate` (respects budget /
  occupancy). Thief server must not expose barrier placement.
- Token auth required for protected calls via an explicit `auth_token` argument
  checked against an env var (documented local dev auth, upgrade for cloud);
  mismatch returns a structured unauthorized result; the real token is never
  logged or returned.
- Dependencies only via uv and pinned; FastMCP preferred; stop and report if the
  API were unclear (it was verified working: FastMCP 3.4.2).

**Dependency decision:** verified FastMCP 3.4.2 API (`FastMCP(name, version)`,
`mcp.tool(fn, name=...)`, `await mcp.list_tools()`, `run(transport="http", host,
port, path)`; `http_app()` builds without binding a socket). Added via
`uv add fastmcp` and pinned `fastmcp>=3.4.2,<4` (uv.lock pins exact 3.4.2 + deps).

**Artifacts produced:**
- `src/mars777_cop_thief/mcp_servers/` — `auth.py`, `common.py`, `tools.py`,
  `cop_server.py`, `thief_server.py`, `run_cop.py`, `run_thief.py`, `__init__.py`.
- `config/mcp.local.default.json`; `.env-example` per-role token/URL placeholders.
- `pyproject.toml` + `uv.lock` (FastMCP pinned).
- Tests under `tests/unit/mcp_servers/` (auth, tools, server builders/adapters,
  run-module import safety, config validation) — 127 tests total, 100% coverage.
- Doc updates: `README.md`, `TODO.md`, `DECISIONS.md` (ADR-0020…ADR-0022),
  `REQUIREMENTS_MATRIX.md`, `ACCEPTANCE_CRITERIA.md`, `PLAN.md`, `SECURITY.md`,
  `COSTS.md`.

**Outcome:** Local HTTP MCP server layer implemented; all quality gates pass
(ruff clean, 127 tests, 100% coverage). No cloud/Gmail/external-LLM/GUI/
inter-group implementation added.

## Stage 6 — Local MCP client & HTTP E2E smoke (2026-06-24)

**Goal:** Prove the local MCP **HTTP transport works end-to-end** by adding a
client/orchestrator that starts the Cop and Thief servers as local subprocesses,
connects over HTTP via the official FastMCP `Client`, and drives a deterministic
flow. **No** cloud, public URLs, Gmail, external-LLM calls, GUI, or inter-group
remote play.

**Key constraints captured from the prompt:**
- The LLM stays outside the servers; game logic stays in the domain; the client
  owns trusted state and calls tools **over HTTP** (not by importing tool
  functions) for the E2E path.
- Two separate local servers on different free `127.0.0.1` ports; tokens/ports
  injected via the child process environment (dummy local values, not committed);
  bounded readiness; always terminate in `finally`.
- Verify auth ± through the client path, hidden opponent never leaks, the thief
  server has no barrier tool, and the result is JSON-serializable.

**FastMCP client decision:** inspected the installed API first
(`fastmcp.Client(url|server)`, async context manager, `call_tool(...).data`,
`list_tools()`, `ping()`); verified a real subprocess HTTP round-trip before
building. **No dependency added** — FastMCP 3.4.2 (already pinned) provides the
client.

**Artifacts produced:**
- `src/mars777_cop_thief/mcp_client/` — `client.py`, `subprocess_pair.py`,
  `e2e_flow.py`, `smoke.py`, `__init__.py`.
- `mcp_servers/common.py` `resolve_port` + `run_cop`/`run_thief` honor
  `COP_MCP_PORT`/`THIEF_MCP_PORT`.
- Tests: `tests/unit/mcp_client/` (URLs, lifecycle with mocks, in-memory flow,
  smoke entry/readiness branches) and `tests/integration/mcp/test_http_e2e.py`
  (real HTTP, default-on, skippable via `RUN_MCP_E2E=0`) — 143 tests, 100% cov.
- Doc updates: `README.md`, `TODO.md`, `DECISIONS.md` (ADR-0023…ADR-0025),
  `REQUIREMENTS_MATRIX.md`, `ACCEPTANCE_CRITERIA.md`, `PLAN.md`, `QUALITY.md`,
  `SECURITY.md`.

**Outcome:** Local MCP HTTP E2E smoke implemented and **passing** over real HTTP
(`uv run python -m mars777_cop_thief.mcp_client.smoke` → exit 0, all checks true);
all quality gates pass (ruff clean, 143 tests, 100% coverage). No
cloud/Gmail/external-LLM/GUI/inter-group implementation added.

> Subsequent stages will append their driving prompts here (protocol over MCP,
> LLM agents, orchestrator, report sender, cloud, bonus, audit).
