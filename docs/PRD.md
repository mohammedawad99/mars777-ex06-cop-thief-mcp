# PRD — Dual AI Agent Cop-and-Thief via MCP (top-level)

**Group:** MaRs-777 (`mars777`) · **Version:** 1.00 · **Status:** Stage 0 draft

## 1. Problem

Build a deterministic, observable Cop-and-Thief grid game in which two
**independent AI agents** (one Cop, one Thief) play against each other. Each
agent perceives the world and acts **only** through an MCP server, using a
natural-language protocol over HTTP. The system must be reproducible, testable,
secure, and produce a verifiable results report.

## 2. Scope

- Game engine: grid world, movement, barriers, capture detection, scoring.
- Two AI agents (Cop, Thief) backed by an LLM.
- Two MCP servers (one per role) exposing perception/action tools over HTTP.
- Natural-language protocol between agent and MCP server.
- Orchestrator that runs `num_sub_games` matches and aggregates results.
- Google/Gmail report sender for final results.
- Inter-group play (bonus) — treated as mandatory architecture (see
  `PRD_bonus_intergroup.md`).
- Configuration, logging, rate limiting, tests, and documentation.

## 3. Non-scope (now)

- No full game logic in Stage 0.
- No MCP server implementation in Stage 0.
- No Gmail/Google API implementation in Stage 0.
- No GUI; a CLI/headless orchestrator is sufficient.
- No multiplayer beyond the defined two-agent / inter-group cases.

## 4. Users & reviewers

- **Players:** the two AI agents.
- **Operators:** team members running matches via uv.
- **Reviewers:** course staff performing strict submission review against the
  rubric and `docs/SUBMISSION_CHECKLIST.md`.

## 5. Functional requirements

- FR1: Configurable grid (default 5×5; sanity sizes 2×2…5×5).
- FR2: 8-direction movement; `stay` disabled unless documented/negotiated.
- FR3: Up to `max_barriers` obstacles; movement blocked by barriers/edges.
- FR4: Capture when Cop and Thief occupy the same cell; visibility radius = 1.
- FR5: Match ends on capture or at `max_moves`; scoring per config.
- FR6: Run `num_sub_games` (default 6) and aggregate scores.
- FR7: Agents act solely through MCP tools over HTTP with token auth.
- FR8: Final results emailed via the Google report sender.

## 6. Non-functional requirements

- NFR1: Reproducible runs via uv; deterministic given a seed.
- NFR2: Each source file < 150 logical lines; ruff-clean; coverage ≥ 85%.
- NFR3: No secrets in Git; token auth for MCP; OAuth files external.
- NFR4: Observable: structured logs, cost/measurement tracking.
- NFR5: Timezone `Asia/Jerusalem` for all timestamps/reports.

## 7. Acceptance criteria

- AC1: `uv sync`, `uv run pytest`, ruff check/format, and coverage gate pass.
- AC2: Default config matches assignment constants.
- AC3: A full match runs end-to-end through MCP and produces a report.
- AC4: Inter-group match runs against another group's server.
- AC5: Submission checklist fully satisfied; gap audit closed.

## 8. Risks

- R1: LLM non-determinism → seed + constrained protocol + retries.
- R2: MCP/HTTP integration drift between groups → shared protocol PRD.
- R3: Cost overruns (LLM/cloud) → rate limits + cost tracking (`COSTS.md`).
- R4: Credential leakage → strict `.gitignore`, `.env-example`, reviews.
- R5: File-size/quality gate regressions → CI-style local gates each stage.
