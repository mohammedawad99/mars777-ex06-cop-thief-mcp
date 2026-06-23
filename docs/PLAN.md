# PLAN — Intended Architecture

**Group:** MaRs-777 · **Status:** Stage 1 (requirements hardening)

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

SDK/shared (done in Stage 0) → requirements hardening (Stage 1) → game engine →
MCP servers (HTTP) → natural-language protocol → agents → orchestrator → report
sender → cloud/self-play → bonus inter-group → hardening & audit.

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
