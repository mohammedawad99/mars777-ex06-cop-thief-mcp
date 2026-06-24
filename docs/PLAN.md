# PLAN — Intended Architecture

**Group:** MaRs-777 · **Status:** Stage 4 (local partial-observability & dialogue)

## Architecture overview

```
                ┌────────────────────────────────────────────┐
                │              Orchestrator                    │
                │  runs N sub-games, seeds RNG, aggregates     │
                └───────┬───────────────────────────┬─────────┘
                        │                            │
                ┌───────▼────────┐          ┌────────▼───────┐
                │   Cop Agent    │          │  Thief Agent   │
                │  (LLM-driven)  │          │  (LLM-driven)  │
                └───────┬────────┘          └────────┬───────┘
                        │ NL protocol / HTTP          │ NL protocol / HTTP
                ┌───────▼────────┐          ┌────────▼───────┐
                │ Cop MCP Server │          │Thief MCP Server│
                └───────┬────────┘          └────────┬───────┘
                        └──────────────┬─────────────┘
                                ┌──────▼───────┐
                                │ Game Engine  │  ← authoritative state
                                └──────┬───────┘
                                ┌──────▼───────┐
                                │ SDK (shared) │  config, version, types
                                └──────┬───────┘
                  ┌────────────┬───────┴────────┬───────────────┐
              results/logs   tests          security        report sender
                                                              (Gmail/OAuth)
```

## Layers

1. **SDK layer** (`sdk/`) — stable façade: version, config loading,
   shared types. Everything depends inward on the SDK, not on each other.
2. **Shared** (`shared/`) — version, safe config loader/validator, constants.
3. **Game engine** — authoritative grid state, movement/barrier rules,
   capture detection, scoring, deterministic stepping.
4. **Agents** — Cop and Thief LLM agents that translate perceptions into
   natural-language intents and parse responses.
5. **MCP servers** — one per role, HTTP transport with token auth, exposing
   perception (`look`) and action (`move`) tools mapped to the engine.
6. **Orchestrator** — runs `num_sub_games`, manages seeds, collects results,
   enforces `max_moves` and rate limits.
7. **Report sender** — Google/Gmail integration sending aggregated results to
   `report_recipient`; OAuth credentials kept outside Git.
8. **Results / logs** — structured logs and per-match results in git-ignored
   `logs/` and `results/local/`.
9. **Tests** — unit (engine rules, config, SDK) and later integration
   (orchestrator, MCP over HTTP) with no external calls in CI.
10. **Security** — token auth, secret hygiene, OAuth revoke story.

## Build order

SDK/shared (Stage 0 ✅) → requirements hardening (Stage 1 ✅) → game engine
(Stage 2 ✅) → local self-play pipeline (Stage 3 ✅) → **local
partial-observability & dialogue (Stage 4 — current)** → MCP servers (HTTP) →
natural-language protocol over MCP → LLM agents → orchestrator over MCP → report
sender → cloud/self-play → bonus inter-group → hardening & audit.

## Pipeline progress (Stage 3)

The pure engine (Stage 2) is now driven by a **local deterministic self-play
pipeline** that is the backbone later stages mirror:

- **Baseline policies** (`agents/baseline.py`) — cop steps toward / thief steps
  away, pure and reproducible (ADR-0015); these sit where LLM agents will later
  plug in behind the same callable contract.
- **Runners** (`orchestration/runner.py`) — `run_sub_game` enforces thief-first
  turn order through the engine, stops on capture or `max_moves`, and records a
  structured event transcript; `run_full_game` repeats for `num_sub_games`.
- **Totals + report** (`orchestration/totals.py`, `report.py`) — an in-memory,
  `json.dumps`-serializable report (ADR-0016), local-only and not emailed
  (`mcp_status: not-deployed`).
- **SDK entrypoints** — `run_local_sub_game` / `run_local_full_game` delegate to
  orchestration; the SDK holds no game logic.

The MCP layer (later) will expose the same engine actions over authenticated
HTTP, keeping the engine authoritative.

## Pipeline progress (Stage 4)

Stage 4 adds a **local partial-observability and natural-language dialogue**
layer over the Stage 3 backbone, establishing the four-way separation that the
MCP/LLM stages will preserve:

- **Full state** — held only by the trusted engine (`game/`).
- **Observation** (`observability/`) — each agent receives a visibility-radius
  (Chebyshev) `Observation`; a hidden opponent's position is `None` and never
  stored, so it cannot leak (ADR-0017).
- **Message text** (`dialogue/messages.py`) — free English describing qualitative
  relative direction; no JSON, no numeric protocol, no exact coordinates
  (ADR-0019).
- **Audit metadata** (`dialogue/transcript.py`) — debug-only evidence kept beside
  the message and never consumed by the other agent (ADR-0018).

The **observed runner** (`orchestration/dialogue_runner.py`) builds an
observation, speaks a message, and acts from the observation only — the engine
still enforces legality and supplies the runner's legal fallback. The Stage 3
full-state runner is preserved for regression. When the LLM/MCP stages arrive,
they consume this same observation contract and message channel; only the
*source* of the message (a model instead of a template) and the *transport* (HTTP
instead of in-process) change.

## Verification artifacts (core)

The **Requirements Matrix** (`REQUIREMENTS_MATRIX.md`) is the project's audit
backbone: every requirement (R-001…R-070) carries a planned response, a concrete
proof artifact, a validation method, and a status. It is the single source of
truth for "what is required" and "is it proven". Two companion documents hang off
it one-to-one:

- `ACCEPTANCE_CRITERIA.md` — measurable pass/fail criteria per delivery area,
  referencing requirement IDs.
- `RISK_REGISTER.md` — delivery/correctness/security risks, each linked to the
  requirement IDs it threatens.

A requirement is only marked `Done` when its proof artifact exists and its
validation method has been run — this is the evidence-first rule (see ADR on
evidence-first delivery), and it directly addresses prior feedback about
unevidenced claims.

## Compatibility architecture (inter-group play)

Inter-group play is mandatory architecture scope (ADR-0005). The seams that make
a foreign group's system interoperable are designed in from the start:

- **HTTP MCP transport, day one** (ADR-0003) — no stdio-only assumptions.
- **Token auth on every tool call** — foreign clients authenticate explicitly;
  match-scoped tokens are revocable after play.
- **Config-driven endpoints** — Cop/Thief URLs (ours or a foreign group's) come
  from config, never hardcoded, so pointing at another team is a config change.
- **Free natural-language messages** between agents stay interoperable because
  they are language, not a brittle wire format; the **engine** remains the
  authority on legality, and an `interpreted_action` is logged beside each raw
  message so cross-group disputes are resolvable from transcripts.
- **Operational coordination** (URL/token exchange, agreed board/origin/turn
  order, 3+3 role-swapped sub-games, report reconciliation, token revocation) is
  specified in `INTERGROUP_BONUS_PROTOCOL.md` — explicitly separate from the
  agent language.

## Evidence artifacts plan

Every claim in the submission is backed by a captured artifact:

- **Results / reports JSON** — per-sub-game and aggregated results in
  git-ignored `results/local/` (and `results/intergroup/` for bonus); internal
  and bonus reports validate against documented schemas.
- **Logs / transcripts** — structured per-turn transcripts (raw NL,
  `interpreted_action`, engine state, illegal-move rejections) in git-ignored
  `logs/`; these are the dispute authority.
- **Validation outputs** — saved output of quality gates (ruff, pytest, coverage,
  file-size, secret scan) per stage, mapped to the matrix `Validation method`.
- **Screenshots** — only where a GUI or cloud/public-URL run is the evidence
  (e.g. a live public endpoint or an inter-group match); not used as a substitute
  for machine-checkable artifacts.
