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

- **AC-MCP-1** (R-002, R-004): Both Cop and Thief MCP servers start over HTTP and
  expose perception (`look`) and action (`move`/`place_barrier`) tools.
- **AC-MCP-2** (R-010): A tool call without a valid token returns 401/403 and is
  logged; a call with a valid token succeeds.
- **AC-MCP-3** (R-005): The orchestrator drives a full local match end-to-end
  through the two HTTP servers and produces a results record.
- **AC-MCP-4** (R-025, R-026): An illegal action submitted via MCP is rejected
  with a structured error and recorded in the transcript.

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

- **AC-NL-1** (R-003): Agent→server and server→agent messages are free natural
  language; transcript inspection finds no fixed numeric/opcode protocol.
- **AC-NL-2** (R-003, R-025): Each NL message is interpreted into a concrete
  action and an `interpreted_action` record is logged alongside the raw text.
- **AC-NL-3** (R-003): An ambiguous or uninterpretable NL message is handled
  deterministically (rejected or clarified) and logged — never silently dropped.

## 6. JSON reports

**Stage 3 status:** an in-memory, `json.dumps`-serializable local report builder
is implemented and test-covered (`orchestration/report.py`,
`tests/unit/orchestration/test_report.py`). It is local-only
(`mcp_status: not-deployed`) and not emailed; schema validation, students, and
MCP URLs are added in later stages.

- **AC-RPT-1** (R-031) — ◑ partially covered: The local report is valid JSON
  (`json.dumps` succeeds in tests); formal schema validation of the final
  submission report is a later stage.
- **AC-RPT-2** (R-033) — ◑ partially covered: The report carries group name/code,
  GitHub repo (placeholder), timezone, sub_games, and totals; students and the
  Cop/Thief MCP URLs are added with the MCP/cloud stages.
- **AC-RPT-3** (R-066): All timestamps in reports are in `Asia/Jerusalem`.

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
