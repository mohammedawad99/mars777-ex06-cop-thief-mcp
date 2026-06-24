# Assignment 6 — Dual AI Agent Cop-and-Thief via MCP

**Group code:** `MaRs-777` &nbsp;|&nbsp; **Technical slug:** `mars777`

A two-agent Cop-and-Thief game where each player is driven by an independent AI
agent. Agents communicate with the game through **MCP servers over HTTP**, using
a natural-language protocol, and the final results are reported via a Google
(Gmail) report sender. Inter-group play is treated as in-scope (see
`docs/PRD_bonus_intergroup.md`).

## Status — Stage 8 (official report schema, validation & evidence pack)

The **official report schema, validation, and a local evidence pack are
implemented** and pass. A stable internal report schema
(`src/mars777_cop_thief/reporting/`) is built from the Stage 7 MCP-backed report,
**validated** (required fields, token-safety, local-URL rule), and is
JSON-only — ready to be an email body later. A **bonus/inter-group schema
example** exists too, but it explicitly makes **no claim that a real inter-group
game has been run** (`bonus_claim: false`, `mutual_agreement: false`).

The reports are **token-safe**: validation rejects any key/value that looks like
`auth_token`, `access_token`, `refresh_token`, `secret`, `password`,
`private_key`, `COP_MCP_TOKEN`/`THIEF_MCP_TOKEN`, or a dummy local token; the
report omits all tokens.

Generate the sanitized, deterministic evidence pack (committed under
`results/evidence/` as `*.example.json` — normalized URLs/timestamp, no tokens,
no full event logs):

```bash
uv run python -m mars777_cop_thief.reporting.generate_evidence_pack
```

This stage is still **local-only**: **Gmail/email sending is not implemented**,
**cloud/public URLs are not deployed**, and the **bonus schema exists but no real
inter-group bonus game has been completed**.

## Status — Stage 7 (MCP-backed local game orchestration)

The **local MCP-backed game orchestration is implemented and passes**: a trusted
orchestrator (`src/mars777_cop_thief/mcp_client/game_flow.py`) plays real
sub-games where **every turn calls the Cop/Thief MCP servers over HTTP** —
`get_observation` → `compose_message` → `propose_action` — then applies the
proposed action through the local game engine (the only authority for legality,
capture, and scoring). The full default game (6 sub-games) runs end-to-end over
HTTP.

The MCP-backed report is JSON-serializable and states **local** status only:
`transport=local_mcp_http`, `mcp_status=local_verified`, local `cop_mcp_url` /
`thief_mcp_url`, `cloud_status=not_deployed`, `email_status=not_sent`, plus
`hidden_state_respected`. The orchestrator may send full state to
`get_observation`, but the server returns only the role-safe filtered observation
and `propose_action` consumes only that — hidden opponent coordinates never leak.

Run the MCP-backed game smoke (starts both servers, plays the full game over
HTTP, prints JSON, exits 0 on pass):

```bash
uv run python -m mars777_cop_thief.mcp_client.game_smoke
```

A real-HTTP one-sub-game integration test runs by default
(`tests/integration/mcp/test_http_game_e2e.py`; skip with `RUN_MCP_E2E=0`). This
stage is still **local-only**: **no public URLs / cloud deployment**, **no
Gmail/email sending**, **no external-LLM calls**, **no GUI**, and **no
inter-group remote play** — those remain later stages.

## Status — Stage 6 (local MCP client & HTTP E2E smoke)

The **local MCP HTTP end-to-end smoke is implemented and passes**: a client
(`src/mars777_cop_thief/mcp_client/`) starts the Cop and Thief servers as local
subprocesses on free `127.0.0.1` ports, connects over **HTTP** with the official
FastMCP `Client`, and drives a deterministic flow — proving the transport works
end-to-end, not just that the tool modules exist.

The smoke verifies, over real HTTP, for **both** roles: `health_check`,
`get_role_info`, valid-token `get_observation`/`compose_message`/`propose_action`,
a wrong-token call returning a structured **unauthorized** result, that a hidden
opponent's position stays `None` (no leak), that messages are plain text, that
actions are structured, and that the **Thief server exposes no barrier tool**.
Servers are always torn down afterward.

Run the local E2E smoke (starts both servers, prints a JSON result, exits 0 on
pass):

```bash
uv run python -m mars777_cop_thief.mcp_client.smoke
```

The real HTTP E2E also runs as a pytest integration test by default
(`tests/integration/mcp/`); set `RUN_MCP_E2E=0` to skip it where local
subprocesses are not allowed. This stage is still **local-only**: **no public
URLs / cloud deployment**, **no Gmail/email sending**, **no external-LLM calls**,
**no GUI**, and **no inter-group remote play**.

## Status — Stage 5 (local HTTP MCP servers)

The **local HTTP MCP server layer is implemented** and unit-tested: two
independent FastMCP servers (Cop and Thief) that expose role-safe tools
delegating to the existing engine / observability / dialogue / policy code
(`src/mars777_cop_thief/mcp_servers/`, exercised by `tests/unit/mcp_servers/`).
The LLM does **not** live in the servers — they only expose tools/resources for a
future client/orchestrator to call.

- Tools (both roles): `get_role_info`, `health_check`, `get_observation`
  (role-safe; hidden opponent never leaked), `compose_message` (free text),
  `propose_action` (observation-based policy). **Cop-only:**
  `place_barrier_candidate`. The **Thief server does not expose barrier
  placement**.
- Transport is **HTTP** (FastMCP `transport="http"`), runnable locally on
  separate ports (Cop `8001`, Thief `8002`) — config in
  `config/mcp.local.default.json`.
- Protected tool calls require a token via an explicit `auth_token` argument
  checked against an environment variable (`COP_MCP_TOKEN` / `THIEF_MCP_TOKEN`).
  This is **local development auth**, to be upgraded for cloud. The real token is
  never logged or returned.

This stage is **local-only**: there are **no public URLs and no cloud deployment
yet**, **no Gmail/email sending**, **no external-LLM calls**, **no GUI**, and **no
inter-group remote play**. Those remain later stages (see `docs/TODO.md`).

Run the local MCP servers (each in its own terminal, after setting tokens in
`.env`):

```bash
uv run python -m mars777_cop_thief.mcp_servers.run_cop     # Cop server  → 127.0.0.1:8001/mcp
uv run python -m mars777_cop_thief.mcp_servers.run_thief   # Thief server → 127.0.0.1:8002/mcp
```

## Status — Stage 4 (local partial-observability & dialogue)

The **local partial-observability and natural-language dialogue layer is
implemented** and unit-tested on top of the Stage 3 self-play backbone:

- **Partial observability** (`observability/`) — each agent receives a
  visibility-radius (Chebyshev) `Observation` that exposes its own role,
  position, the board, move counts, locally visible barriers, and (for the cop)
  its barrier budget. The opponent's position is included **only when within the
  radius**; otherwise it is `None` and the hidden coordinate is never stored.
- **Natural-language dialogue** (`dialogue/`) — agents emit **free English**
  messages (not JSON, not a numeric protocol) that describe qualitative,
  relative spatial sense ("I can see movement nearby; the opponent seems close to
  the south-east", "I cannot see the thief right now"). A transcript records each
  message plus debug-only audit facts that the other agent never consumes.
- **Observed runner** (`orchestration/dialogue_runner.py`) — observation-based
  policies act only on what they can see (cop steps toward a visible thief, else
  patrols; thief flees a visible cop, else explores), and the trusted engine
  still enforces legality.

The earlier deterministic **full-state self-play backbone (Stage 3) is preserved**
for regression. Nothing contacts an external service. There is still **no MCP
server, no HTTP endpoint, no external-LLM understanding, no Gmail/Google
integration, no cloud deployment, and no inter-group networking** — those are
later stages (see `docs/TODO.md`). Reports remain local-only
(`mcp_status: not-deployed`) and are **not emailed**.

Run a local self-play game (full-state backbone, prints the JSON report):

```bash
uv run python -c "import json; from pathlib import Path; from mars777_cop_thief.sdk import AssignmentSdk; print(json.dumps(AssignmentSdk().run_local_full_game(Path('config/game.default.json')), indent=2))"
```

Run a local observed/dialogue game (partial observability + transcript):

```bash
uv run python -c "import json; from pathlib import Path; from mars777_cop_thief.sdk import AssignmentSdk; print(json.dumps(AssignmentSdk().run_local_dialogue_full_game(Path('config/game.default.json')), indent=2))"
```

See `docs/TODO.md` for the staged roadmap and `docs/FINAL_GAP_AUDIT.md` (not
final yet) for the closing audit plan.

### Planning & verification artifacts

Requirements hardening (Stage 1) is captured in a set of audit documents:

- `docs/REQUIREMENTS_MATRIX.md` — the audit backbone: every requirement
  (R-001…R-070) with its planned response, proof artifact, validation method,
  and status. A requirement is only `Done` when its evidence exists.
- `docs/ACCEPTANCE_CRITERIA.md` — measurable pass/fail criteria per delivery area.
- `docs/RISK_REGISTER.md` — delivery, correctness, and security risks with
  mitigations and triggers.
- `docs/INTERGROUP_BONUS_PROTOCOL.md` — operational coordination for the
  (mandatory-scope) inter-group bonus; not a hardcoded agent message protocol.

## Repository layout

```
config/    default JSON config (game, rate limits, logging)
docs/      PRDs, plan, decisions, quality/cost/security docs
src/mars777_cop_thief/
  constants.py        shared identifiers and required-key lists
  sdk/sdk.py          AssignmentSdk façade (stable entry point)
  shared/version.py   single source of version truth ("1.00")
  shared/config.py    safe JSON config loader + validator
  game/               pure game engine: models, rules, state, engine, events
  agents/             deterministic baseline + observation-based policies
  observability/      visibility helpers and per-agent partial observations
  dialogue/           natural-language message generation + transcript records
  orchestration/      full-state and observed/dialogue runners, totals, report
  mcp_servers/        local HTTP MCP servers (Cop/Thief), auth guard, tools
  mcp_client/         local MCP client, server-pair lifecycle, E2E + game flow
  reporting/          official report schema, validation, evidence pack writer
results/evidence/     sanitized, deterministic example artifacts (*.example.json)
tests/unit/           version, config, and SDK smoke tests
tests/unit/game/      engine TDD suite (models, rules, engine, events, SDK)
tests/unit/agents/    baseline + observed policy tests
tests/unit/observability/  visibility and observation tests
tests/unit/dialogue/  message and transcript tests
tests/unit/orchestration/  runner, dialogue runner, report, and SDK tests
tests/unit/mcp_servers/    auth, tools, server-builder, run/config tests
tests/unit/mcp_client/     client URLs, lifecycle, in-memory flow, smoke entry
tests/integration/mcp/     real HTTP end-to-end smoke (default-on)
tests/unit/reporting/      schema validation, official report, evidence tests
```

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (the **only** package manager used here)

> This project uses **uv exclusively**. Do not use `pip`, `python -m`,
> `requirements.txt`, `virtualenv`, or `venv`.

## Install & validate

```bash
# 1. Install dependencies (creates the managed environment)
uv sync

# 2. Format and lint
uv run ruff format .
uv run ruff check .

# 3. Run tests
uv run pytest

# 4. Run tests with coverage (gate: fail_under = 85)
uv run pytest --cov=src --cov-report=term-missing

# 5. File-size check (each source file must stay < 150 logical lines)
find src tests -name "*.py" -print0 | xargs -0 wc -l

# 6. Secret / artifact scan
git status --short --ignored
```

The full list of quality gates lives in `docs/QUALITY.md`.

## Security

No secrets are committed. Copy `.env-example` to `.env` for local runs and keep
Google OAuth files (`credentials.json`, `token.json`) out of Git. See
`docs/SECURITY.md`.
