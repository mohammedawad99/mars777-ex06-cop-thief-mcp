# PLAN — Intended Architecture

**Group:** MaRs-777 · **Status:** Stage 0 draft

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

SDK/shared (done in Stage 0) → game engine → MCP servers (HTTP) → agents →
orchestrator → report sender → bonus inter-group → hardening & audit.
