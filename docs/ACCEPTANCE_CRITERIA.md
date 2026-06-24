# ACCEPTANCE CRITERIA

**Group:** MaRs-777 (`mars777`) · **Stage:** 1 · **Status:** Baseline definition

Measurable, testable criteria per delivery area. Each criterion is written so a
reviewer can mark it pass/fail without interpretation. IDs map back to
`REQUIREMENTS_MATRIX.md` (`R-0xx`). "Given/When/Then" is used where behaviour is
non-trivial.

---

## 1. Local game engine

**Stage 2–3 status:** the pure engine core is implemented and unit-tested
(`tests/unit/game/`); Stage 3 adds a deterministic local self-play pipeline
(`tests/unit/agents/`, `tests/unit/orchestration/`). AC-ENG-1…AC-ENG-5 are
test-covered below; AC-ENG-6 has per-game scoring covered and a totals aggregator
(`orchestration/totals.py`) with an explicit `[30,90]` property test still to be
added; AC-ENG-7 holds for the engine and policies (parameters read from config)
with a full repo-wide grep audit ongoing; AC-ENG-8 — baseline self-play is fully
deterministic (no RNG), with seed hooks deferred until randomness is introduced.

- **AC-ENG-1** (R-011, R-017) — ✅ test-covered: Given a Cop and Thief on the same
  cell after a turn, when the engine evaluates terminal state, then it reports
  `cop_win` (either player moving onto the other).
- **AC-ENG-2** (R-018) — ✅ test-covered: Given `max_moves` moves elapse with no
  capture, then the engine reports `thief_win`.
- **AC-ENG-3** (R-019, R-020) — ✅ test-covered: Each of the 8 compass moves from a
  non-edge cell is accepted; a `stay` action is rejected when `allow_stay=false`.
- **AC-ENG-4** (R-021–R-024) — ✅ test-covered: A Cop barrier counts as the Cop's
  turn; placement beyond the barrier limit is rejected; a Thief barrier attempt is
  rejected; moving into a barrier cell is rejected.
- **AC-ENG-5** (R-014) — ✅ test-covered: The engine runs cleanly for grid sizes
  2×2, 3×3, 4×4, and 5×5 (parametrized test passes for all four).
- **AC-ENG-6** (R-027–R-030): Scoring matches config exactly; over 6 sub-games the
  team total is always within `[30, 90]`.
- **AC-ENG-7** (R-013, R-055): No game parameter is a literal in engine code; all
  come from loaded config (grep audit finds none).
- **AC-ENG-8** (R-068): Two runs with the same seed produce byte-identical
  transcripts.

## 2. Local MCP over HTTP

**Stage 5–6 status:** two local FastMCP servers (HTTP transport) are implemented
and, in Stage 6, **proven end-to-end over real HTTP** by a client that starts both
servers as subprocesses and drives a deterministic flow (`mcp_servers/`,
`mcp_client/`, `tests/unit/mcp_servers/`, `tests/unit/mcp_client/`,
`tests/integration/mcp/`). The thief server omits barrier placement; observations
never leak the hidden opponent. Auth is an explicit `auth_token` checked against
an env var (local dev auth). The over-the-wire **game** orchestrator drive (agents
playing a full match through MCP) is a later stage.

- **AC-MCP-1** (R-002, R-004) — ✅ test-covered (real HTTP): The E2E smoke starts
  both Cop and Thief servers on free local ports and calls each over HTTP
  (`health_check`, `get_role_info`, `get_observation`, `compose_message`,
  `propose_action`; cop-only `place_barrier_candidate`); the smoke command exits 0
  with all checks true.
- **AC-MCP-2** (R-010) — ✅ test-covered (real HTTP + unit): a protected tool call
  with a wrong token returns a structured unauthorized result (and never reveals
  the token) through the client path; a matching token succeeds. (Local dev auth;
  HTTP-status mapping arrives with the cloud stage.)
- **AC-MCP-3** (R-005) — ✅ test-covered (real HTTP, Stage 7): the orchestrator
  drives a full local game (6 sub-games) end-to-end through the two HTTP servers —
  each turn calls `get_observation`/`compose_message`/`propose_action` over HTTP —
  and produces a JSON-serializable report with local status fields. The
  `game_smoke` command exits 0 with all checks true.
- **AC-MCP-4** (R-025, R-026) — ◑ partially (Stage 7): an MCP-proposed action the
  engine rejects is recorded as a not-ok event and replaced by a deterministic
  legal fallback (tested). Full natural-language interpreted-action dispute logs
  arrive with the LLM-agent stage.

## 3. Cloud / self-play

- **AC-CLOUD-1** (R-006, R-009): Both servers are reachable at public Cop and
  Thief URLs; a match runs end-to-end against those URLs.
- **AC-CLOUD-2** (R-010): The public URLs reject unauthenticated requests
  (verified from an external client).
- **AC-CLOUD-3** (R-006): A reproducible run command and its output (logs +
  results JSON) are captured as evidence of the cloud run.

## 4. Inter-group bonus

- **AC-BONUS-1** (R-007): A match completes against another group's MCP server
  using config-provided foreign URLs and exchanged tokens.
- **AC-BONUS-2** (R-070): Both groups run 3 sub-games one way and 3 with roles
  swapped, per `INTERGROUP_BONUS_PROTOCOL.md`.
- **AC-BONUS-3** (R-034): A bonus report is produced containing both group names,
  both repos, four URLs, students, sub_games, totals_by_group, bonus_claim, and
  mutual_agreement.
- **AC-BONUS-4** (R-035): When the two groups' reports disagree, `mutual_agreement`
  is `false` and `bonus_claim` is not asserted as accepted.
- **AC-BONUS-5** (R-070): Tokens used for the match are revoked after play, and the
  revocation is recorded.

## 5. Natural-language protocol

**Stage 4 status:** a **local** partial-observability and free natural-language
dialogue layer is implemented and test-covered (`observability/`, `dialogue/`,
`orchestration/dialogue_runner.py`; `tests/unit/observability/`,
`tests/unit/dialogue/`). Messages are plain English with qualitative relative
direction and no coordinates; the opponent's position is hidden outside the
visibility radius and never leaks; audit metadata is kept separate from message
text. The MCP transport and model-driven interpretation are later stages.

- **AC-NL-1** (R-003) — ✅ test-covered (local): Messages are free natural
  language; tests assert plain strings (not JSON) and qualitative wording with no
  numeric coordinates.
- **AC-NL-2** (R-003, R-025) — ◑ partially: each turn records a structured event
  and a transcript message with debug-only audit facts; model-driven
  `interpreted_action` over MCP arrives in a later stage.
- **AC-NL-2b** (R-003, R-040) — ✅ test-covered (Stage 9): a prompted MCP game runs
  end-to-end where an LLM agent (offline `fake_local` provider) receives the
  role-safe observation, emits a natural-language `ACTION:` line, and the parser
  extracts the action; a parse/legality failure is recorded
  (`parse_failures`/`fallbacks_used`) and replaced by a deterministic legal
  fallback. Prompts/responses never contain hidden opponent coordinates.
- **AC-NL-3** (R-003): An ambiguous or uninterpretable NL message is handled
  deterministically (rejected or clarified) and logged — later stage (model
  interpretation not yet implemented).

### Partial observability (Stage 4, local)

- **AC-PO-1** (R-067) — ✅ test-covered: the opponent is visible within
  `visibility_radius` (Chebyshev) and hidden outside it.
- **AC-PO-2** (R-067) — ✅ test-covered: a hidden opponent's coordinate is never
  present in the observation (`opponent_position is None`; absent from `to_dict`).
- **AC-PO-3** (R-067) — ✅ test-covered: observation-based policies decide from the
  observation only (no hidden-state cheating), with deterministic patrol/explore
  fallback when the opponent is hidden.

## 6. JSON reports

**Stage 8 status:** an official internal report schema is built from the
MCP-backed report and **validated** (required fields, token-safety, local-URL
rule); a bonus schema example exists (no real run claimed); a sanitized,
deterministic evidence pack is generated and committed
(`reporting/`, `tests/unit/reporting/`, `results/evidence/*.example.json`).
Email sending itself is still a later stage.

- **AC-RPT-1** (R-031) — ✅ test-covered: The official internal report is valid
  JSON (`json.dumps` succeeds) and passes schema validation
  (`validation_status: valid`); it is **email-body ready** (JSON only, no prose).
- **AC-RPT-2** (R-033) — ✅ test-covered: The report carries group name/code,
  students (configurable), GitHub repo, Cop/Thief MCP URLs, timezone, config
  summary, sub_games, and totals; required-field validation enforces them.
- **AC-RPT-3** (R-066): All timestamps in reports are in `Asia/Jerusalem`
  (evidence normalizes `generated_at_iso` to a placeholder for determinism).
- **AC-RPT-4** (R-034) — ◑ partially: a bonus schema **example** validates and
  carries all required fields, but explicitly makes no real-run claim
  (`bonus_claim: false`); a real inter-group bonus game is a later stage.
- **AC-RPT-5** (R-065) — ✅ test-covered: validation rejects token-like keys/values
  and dummy tokens; the committed evidence pack is sanitized and token-free.

## 7. Email sending

- **AC-MAIL-1** (R-032): The email body sent to the instructor is structured JSON
  only — no free-text prose (verified on the outbound payload fixture).
- **AC-MAIL-2** (R-037): Sending uses the Gmail API (or a documented alternative)
  through the API gatekeeper layer; a dry-run path exists for testing without
  sending.
- **AC-MAIL-3** (R-036): No OAuth credential or token is read from inside the repo
  tree; all come from environment/external paths.

## 8. Security

- **AC-SEC-1** (R-010): No MCP endpoint is reachable without a token in any
  environment (local, cloud, inter-group).
- **AC-SEC-2** (R-036, R-053): A secret-pattern scan of the repo (excluding
  `.git`/caches) returns no matches; `git status --ignored` shows OAuth files
  untracked.
- **AC-SEC-3** (R-057): All external API egress flows through the API gatekeeper
  module; no ad-hoc network calls elsewhere.
- **AC-SEC-4** (R-070): Inter-group tokens are exchanged out-of-band and revoked
  after the session.

## 9. Documentation

- **AC-DOC-1** (R-044–R-048): README at root plus `PRD.md`, `PLAN.md`, `TODO.md`,
  and mechanism PRDs all present and current.
- **AC-DOC-2** (R-038, R-039): README is professional and contains the Dec-POMDP
  framing with the full tuple ⟨n, S, {A_i}, P, R, {Ω_i}, O, γ⟩ mapped to the game.
- **AC-DOC-3** (R-060, R-065): `PROMPTS.md` records each stage's driving prompt;
  every quality claim in docs cites a proof artifact.

## 10. Quality gates

- **AC-QG-1** (R-050): `uv run ruff check .` reports zero violations.
- **AC-QG-2** (R-050): `uv run ruff format --check .` reports no changes needed.
- **AC-QG-3** (R-051): `uv run pytest --cov=src` reports coverage ≥ 85% and the
  suite passes.
- **AC-QG-4** (R-052): Every `.py` file in `src/` and `tests/` is ≤ 150 code lines.
- **AC-QG-5** (R-049): Only uv is used; no `pip`, `requirements.txt`, or `venv`
  artifacts are present.
- **AC-QG-6** (R-063): The final gap audit is completed and every open gap is
  either closed or explicitly justified before submission.

---

### Pass/fail discipline

A delivery area is "accepted" only when **all** its criteria pass with captured
evidence. Partial passes are recorded as `In progress` in the Requirements Matrix,
never rounded up to `Done`.
