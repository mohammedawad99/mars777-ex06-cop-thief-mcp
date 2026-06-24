# PLAN — Intended Architecture

**Group:** MaRs-777 · **Status:** Stage 13B (live-readiness preflight; no live send/deploy)

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
(Stage 2 ✅) → local self-play pipeline (Stage 3 ✅) → local
partial-observability & dialogue (Stage 4 ✅) → local HTTP MCP servers (Stage 5
✅) → local MCP client & HTTP E2E smoke (Stage 6 ✅) → MCP-backed local game orchestration (Stage 7 ✅) → official report schema, validation & evidence (Stage 8 ✅) → prompted MCP agent layer (Stage 9 ✅; offline fake LLM) → optional Gemini
provider (Stage 10 ✅; live-gated) → Gmail JSON report sender (Stage 11 ✅;
dry-run + live-gated) → hardened run validation (Stage 12 ✅) → cloud deployment
packaging & preflight (Stage 13A ✅) → **live-readiness preflight (Stage 13B —
current; read-only, no live send/deploy)** → live cloud deploy (13C) → bonus
inter-group → hardening & audit.

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

## Pipeline progress (Stage 5)

Stage 5 adds the **local HTTP MCP server layer** (`mcp_servers/`) on top of the
domain packages, preserving the four-way separation from Stage 4:

- **Two role-separated FastMCP servers** (`cop_server`/`run_cop`,
  `thief_server`/`run_thief`) over HTTP transport on separate local ports
  (ADR-0020). The **thief server omits barrier placement** (ADR-0022).
- **Pure tool adapters** (`tools.py`) delegate to engine / observability /
  dialogue / observed-policy code and return JSON-safe payloads; the LLM lives in
  the future client, not the server, and game logic stays in the domain.
- **Role-safe observations** — the `get_observation` tool returns the Stage 4
  `Observation` (hidden opponent stays `None`), so the transport cannot leak
  hidden state.
- **Token auth guard** (`auth.py`) — protected tools require an `auth_token`
  checked against an env var (local dev auth, ADR-0021); failures are structured
  and the token is never logged/returned.

The next stage wires natural-language message interpretation and interpreted
actions through these tools; cloud/public-URL exposure and Gmail sending remain
later, explicitly out of Stage 5.

## Pipeline progress (Stage 6)

Stage 6 adds the **local MCP client/orchestrator** (`mcp_client/`) and proves the
HTTP transport works end-to-end:

- **Server-pair lifecycle** (`subprocess_pair.py`) — starts both servers as
  short-lived `127.0.0.1` subprocesses on free ports, injects dummy local tokens
  and ports via the child environment, and always tears them down (ADR-0023).
- **Client helpers** (`client.py`) — official FastMCP `Client`, URL builders, and
  a bounded `wait_ready` ping-based readiness check.
- **Deterministic flow** (`e2e_flow.py`) — one flow reused for in-memory (fast
  tests) and real HTTP (smoke + integration), returning a JSON-serializable result
  (ADR-0024). It calls each role's tools over HTTP and asserts auth ±, hidden-state
  isolation, plain-text messages, structured actions, and thief-no-barrier.
- **Smoke entrypoint** (`smoke.py`) — `uv run python -m
  mars777_cop_thief.mcp_client.smoke`, exits 0 only when every check passes.

This closes the loop from engine → observation → message → MCP tool → **real HTTP
client call**. The LLM/agent drive over MCP, cloud exposure, and Gmail remain
later and are explicitly out of Stage 6.

## Pipeline progress (Stage 7)

Stage 7 turns the Stage 6 transport into a **real game pipeline** — the
orchestrator plays full games where every turn goes through the MCP servers:

- **`game_flow.py`** — `run_mcp_sub_game`/`run_mcp_full_game`: the trusted
  orchestrator holds authoritative state; each turn calls
  `get_observation`→`compose_message`→`propose_action` over the client, converts
  the proposal to an engine `Action`, and applies it through the engine (sole
  authority). Illegal proposals are recorded and replaced by a legal fallback
  (ADR-0026).
- **`game_report.py`** — `build_mcp_report` adds explicit local status fields
  (`transport`, `mcp_status`, urls, `cloud_status`, `email_status`,
  `hidden_state_respected`) and never stores tokens (ADR-0027).
- **`game_smoke.py`** — `uv run python -m mars777_cop_thief.mcp_client.game_smoke`
  plays the full default game over HTTP and exits 0 only when every check passes.

Hidden-state isolation holds end-to-end: the orchestrator may pass full state to
`get_observation`, but the server returns only the role-safe observation and
`propose_action` consumes only that — the transcript carries no hidden
coordinates. LLM agents will later replace the observed policy behind the same
tool contract; cloud exposure, Gmail, and inter-group play remain out of Stage 7.

## Pipeline progress (Stage 8)

Stage 8 turns the operational MCP-backed report into a **submission-grade,
validated, token-safe report** plus committed evidence (`reporting/`):

- **`schemas.py` / `validators.py`** — stable required-field sets and a recursive
  token-safety scan; local URLs allowed only when `cloud_status` is
  local/not_deployed; cloud URLs accepted but not required (ADR-0028/0029).
- **`official_report.py`** — `build_official_internal_report` transforms the
  Stage 7 report into the stable internal schema (summarised transcripts,
  `event_count` instead of raw events, students/evidence/validation_status), and
  `build_bonus_report_example` provides a bonus schema that claims no real run.
- **`evidence.py` / `generate_evidence_pack.py`** — write a sanitized,
  deterministic pack (normalized URLs/timestamp, summary, ≤4-message excerpt,
  no full logs) under `results/evidence/`, refusing any token-like content.

The report is now JSON-only and email-body ready; the **report sender (Gmail)**
that actually emails it remains a later stage, as do cloud exposure and a real
inter-group bonus game.

## Pipeline progress (Stage 9)

Stage 9 adds a **provider-agnostic LLM-agent layer** (`llm/`) and a **prompted**
MCP-backed game, making the architecture LLM-ready while staying offline and
deterministic:

- **Provider interface + `fake_local`** (`provider.py`, `fake_provider.py`) — a
  minimal `complete(...)` contract and a deterministic offline provider that
  reasons over the role-safe observation and emits `ACTION: move <direction>`
  (ADR-0030). A real provider can later implement the same interface (keys via
  env, opt-in).
- **Prompts + parser + cost** (`prompts.py`, `parser.py`, `cost.py`) — role
  prompts with qualitative opponent direction (no hidden coordinates, no
  secrets); a safe `ACTION:` parser; non-negative token/cost estimates.
- **Prompted flow** (`mcp_client/prompted_game_flow.py`) — per turn:
  `get_observation` → `compose_message` → build prompt → provider → parse →
  engine, with a deterministic fallback on parse/legality failure (ADR-0032),
  recording prompt summary, response, parse status, tokens, cost, and
  `fallback_used`. The provider lives on the client side, never in the servers
  (ADR-0031).

The report gains `llm_mode`/provider/token/cost/`parse_failures`/`fallbacks_used`
fields. Real external LLM calls, cloud exposure, Gmail, and inter-group play
remain out of Stage 9.

## Pipeline progress (Stage 10)

Stage 10 makes the provider layer **real-LLM-ready** with an **optional** Gemini
adapter, without requiring or committing any key:

- **`llm/gemini_provider.py`** — `GeminiProvider` over the official `google-genai`
  SDK (single non-streaming `generate_content`, small output cap, no tools);
  reports actual usage tokens when present, else the estimator; the key is held
  privately and never logged/returned/in metadata (ADR-0033).
- **`llm/config.py` + `llm/provider_factory.py`** — config holds only env-var
  *names*; `create_provider_from_env` defaults to `fake_local` and selects Gemini
  only when requested with a key, else raises a controlled error; no import-time
  API calls (ADR-0034).
- **`mcp_client/gemini_prompted_smoke.py`** — live-gated (`RUN_GEMINI_LIVE=1`),
  skips cleanly by default, runs one short bounded sub-game when enabled, never
  prints the key (ADR-0035). Unit tests mock the SDK; no live calls in pytest.

`fake_local` stays the default deterministic path; the real Gemini smoke is
opt-in, cost-bounded, and was not run here. Cloud exposure, Gmail, and
inter-group play remain out of Stage 10.

## Pipeline progress (Stage 11)

Stage 11 makes the validated official report **sendable by the Gmail API**,
safely (`gmail/`):

- **`mime_builder.py`** — the email **body is JSON only** (exactly
  `json.dumps(report, ensure_ascii=False, indent=2)`); base64url raw message; a
  test decodes it and asserts the body parses back to the report (ADR-0037).
- **`config.py` / `auth.py`** — config holds only env-var *names*; OAuth
  credential/token paths come from the environment and live **outside the repo**;
  the loader refreshes/flows lazily with injected deps and never logs secret
  content; the minimal `gmail.send` scope is used (ADR-0038).
- **`sender.py` / `send_report.py`** — dry-run by default (no API call); live
  sending only when `RUN_GMAIL_LIVE=1`, with a controlled failure when
  credentials are missing; `SendResult` is JSON-serializable and carries no
  secrets (ADR-0036). The live Gmail send is opt-in and was not run here.

The report is now both **email-body ready** (Stage 8) and **sendable** (Stage 11).
Cloud exposure and a real inter-group bonus game remain out of Stage 11.

## Pipeline progress (Stage 12)

Stage 12 wraps the working pipeline in a **reproducibility/audit layer**
(`run/`):

- **Deterministic identity + manifest** (`identity.py`, `manifest.py`) — `run_id`
  from group/stage/config-hash/seed (ADR-0039); a JSON manifest of enabled vs
  not-yet capabilities, gates, and scan status, provably secret-free (ADR-0040).
- **Classified failures + bounded retries** (`status.py`, `retry.py`,
  `rate_limit.py`) — 12 categories with redaction, and a validated,
  config-driven retry/timeout policy + resource guard (ADR-0041).
- **Aggregate validation + hardened smoke** (`validation.py`,
  `hardened_smoke.py`) — validates the full report (count/totals/winners/
  status/tokens/URLs) and gates programmatic quality checks, emitting a JSON
  summary with the manifest. No secrets, no raw logs.

The pipeline is now reproducible and auditable. The next stages (cloud/public
URLs, real inter-group bonus, live Gmail send) reuse this manifest and validation
unchanged.

## Pipeline progress (Stage 13A)

Stage 13A prepares a **controlled cloud deployment** of the two MCP servers
without performing it (`deployment/`, `Dockerfile`, `cloud_entrypoint.py`):

- **One role-aware image** (ADR-0042/0043) — `MCP_ROLE` selects cop/thief, binds
  `0.0.0.0`, reads `PORT`, and fails fast if the role's token env var is missing
  (name only, never the value); local mode still binds `127.0.0.1`.
- **Cloud config + placeholders** — `config/cloud.default.json` (Cloud Run target,
  service names, env-var names, `<set-after-deployment>` URLs,
  `cloud_status: not_deployed`); `.dockerignore` keeps secrets/caches/tests out of
  the image.
- **Preflight before live deploy** (ADR-0044) — validates packaging readiness with
  **no cloud calls, no gcloud, no credentials**; the deploy script is an inert,
  `RUN_CLOUD_DEPLOY=1`-gated template with placeholders only.

**No Cloud Run service was created and no public URL exists.**

## Pipeline progress (Stage 13B — live-readiness preflight)

Stage 13B adds a **read-only bridge** from local implementation to live operations
(`deployment/live_readiness.py`, `deployment/gcloud_checks.py`, `gmail/preflight.py`)
— it deploys nothing and sends no live Gmail (ADR-0045/0046):

- **Gmail OAuth readiness** — checks `GOOGLE_OAUTH_CLIENT_SECRETS` /
  `GOOGLE_OAUTH_TOKEN_PATH` paths exist **outside** the repo by stat only; never
  reads contents; `live_send_enabled=false` unless `RUN_GMAIL_LIVE=1`. The external
  OAuth files are present (manual smoke succeeded) and stay out of Git.
- **Read-only cloud checks** — `gcloud` install, active account presence, active
  project vs `api-mars-777`, intended region (`CLOUD_RUN_REGION`, recommended
  `me-west1`), best-effort billing; missing gcloud / no auth / project mismatch /
  billing-disabled are **blockers**, billing-unknown a **warning** — never a crash.
  No `deploy`/`build`/`create`/`enable` command is ever run.
- **Combined readiness** — folds in the packaging preflight and lists the exact
  remaining manual actions; exits `0` once checks complete even with blockers.

The **next** stage (manual, gated live deploy) records real URLs locally and flips
`cloud_status`; the hardened validation/manifest and the role-safe boundary carry
over unchanged.

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
