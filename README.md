# Assignment 6 — Dual AI Agent Cop-and-Thief via MCP

**Group code:** `MaRs-777` &nbsp;|&nbsp; **Technical slug:** `mars777`

A two-agent Cop-and-Thief game where each player is driven by an independent AI
agent. Agents communicate with the game through **MCP servers over HTTP**, using
a natural-language protocol, and the final results are reported via a Google
(Gmail) report sender. Inter-group play is treated as in-scope (see
`docs/PRD_bonus_intergroup.md`).

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
tests/unit/           version, config, and SDK smoke tests
tests/unit/game/      engine TDD suite (models, rules, engine, events, SDK)
tests/unit/agents/    baseline + observed policy tests
tests/unit/observability/  visibility and observation tests
tests/unit/dialogue/  message and transcript tests
tests/unit/orchestration/  runner, dialogue runner, report, and SDK tests
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
