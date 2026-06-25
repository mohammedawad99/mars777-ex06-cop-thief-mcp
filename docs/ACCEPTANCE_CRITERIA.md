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

**Stage 13C/14A status:** both MCP services are **deployed live** to Cloud Run
(`api-mars-777` / `me-west1`) at public URLs with **app-level token auth**; public
HTTPS smoke passes and a **full 6-sub-game game + official report dry-run** runs over
those public URLs (Stage 14A). Packaging/preflight from 13A–13B remain green. The
packaging template `config/cloud.default.json` is intentionally left `not_deployed`
as a reusable pre-deploy gate; live state is in
`results/evidence/cloud_deployment.example.json` and the public-cloud report
evidence. **No live Gmail report, no inter-group bonus run, and no final
submission** yet.

- **AC-CLOUD-0** (R-006) — ✅ test-covered: `deployment.preflight` validates the
  config, Dockerfile/.dockerignore, absence of secret files, placeholder URLs, and
  role/port resolution without starting a server → `status: ok`.
- **AC-CLOUD-0b** (R-006, R-037) — ✅ test-covered (Stage 13B): `deployment.live_readiness`
  combines a Gmail OAuth external-file check (paths/existence/outside-repo only, no
  content read), read-only `gcloud`/Cloud Run checks (install, account, project vs
  `api-mars-777`, region `me-west1`, best-effort billing), and the packaging
  preflight into one JSON report. It exits `0` with blockers listed and performs
  **no live send and no deploy**. Blockers/warnings never crash. Mocked/temp-file
  tests make no network call.
- **AC-CLOUD-1** (R-006, R-009) — ✅ real (Stage 13C): both servers are reachable at
  public Cop and Thief Cloud Run URLs; the deterministic E2E flow runs over HTTPS
  against those URLs and passes (`scripts/public_cloud_smoke.py` → `passed: true`).
- **AC-CLOUD-2** (R-010) — ✅ real (Stage 13C): protected tools reject a wrong/absent
  token with a structured `unauthorized` result (verified over the public URLs); IAM
  is public **only** because the app enforces the token (raw `GET /mcp` → `406`, not
  an IAM `403`).
- **AC-CLOUD-3** (R-006) — ✅ real (Stage 13C): a reproducible smoke command and its
  sanitized output are captured in `results/evidence/cloud_deployment.example.json`
  (URLs, revisions, smoke statuses; no token values).
- **AC-CLOUD-4** (R-005, R-031, R-033) — ✅ real (Stage 14A): a **full 6-sub-game
  game** runs over the public `/mcp` URLs (`scripts/public_cloud_final_dry_run.py`);
  the **official internal report** is built with the public URLs + repo +
  `cloud_status: deployed`, **schema-validates** (`validation_status: valid`), and
  passes the Gmail sender in **dry-run only** (`dry_run`, `body_json_valid: true`).
  Evidence: `results/evidence/public_cloud_full_game.example.json` and
  `final_report_dry_run.example.json` (no tokens). **No live email was sent.**

## 4. Inter-group bonus

- **AC-BONUS-0** (R-007) — ✅ test-covered (Stage 15A): a readiness gate
  (`scripts/bonus_partner_readiness.py`) validates our own cloud readiness and a
  local git-ignored partner intake file, and runs a partner compatibility smoke when
  the partner endpoints/tokens are real. It exits 0 with `bonus_ready: false` and
  explicit blockers while the partner is pending; the pure intake validation is
  unit-tested (`tests/unit/bonus/`). Evidence is token-free and ID-free
  (`results/evidence/bonus_readiness.example.json`). **Readiness is prepared, not the
  bonus game itself.**
- **AC-BONUS-1** (R-007) — ✅ done (Stage 15D): the official match completed against
  orcai-mj's live MCP servers using the local partner URLs/tokens — an automated
  referee drove all moves (no human), our `GameEngine` canonical on 8x8; 6/6 sub-games
  decided (`scripts/run_bonus_game.py`, `results/evidence/bonus_game_official_run.example.json`).
- **AC-BONUS-2** (R-070) — ✅ done (Stage 15D): both pairing directions ran — Set A (3)
  MaRs-777 Cop vs orcai-mj Thief and Set B (3) orcai-mj Cop vs MaRs-777 Thief, per
  `INTERGROUP_BONUS_PROTOCOL.md`. The orchestration supports both; neither was faked.
- **AC-BONUS-3** (R-034) — ✅ done (Stage 15D): the canonical `bonus_game` report carries
  both group names, both repos, four public URLs, students (IDs redacted in tracked
  evidence), pairing-labelled `sub_games`, `totals_by_group` (MaRs-777 30 / orcai-mj 90),
  `bonus_claim`, `mutual_agreement`, and a `result_hash`; `validation_status: valid`.
- **AC-BONUS-4** (R-035) — ✅ done (Stage 15E): partner orcai-mj confirmed the canonical
  result and rules in writing, so `mutual_agreement: true` and
  `partner_confirmation_status: confirmed` are finalized (`bonus/finalize.py`) **without
  changing any result field**; `result_hash` is unchanged (`a0fdf72d…`) and the final
  handoff/evidence ship a derived `hash_method` (sha256, canonical JSON, included/excluded
  fields, 3-step recipe) the partner can reproduce. The validator still rejects a premature
  `mutual_agreement=true` (unit-tested). Final artifacts: `bonus_game_report_final_agreed`,
  `bonus_game_partner_handoff_final`, `bonus_game_mutual_agreement`.
- **AC-BONUS-5** (R-070) — ⏳ open: match-scoped tokens are revoked after play and the
  revocation recorded (post-confirmation step; tokens stay in the git-ignored file only).

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
- **AC-NL-2c** (R-001, R-061) — ✅ test-covered (Stage 10): an **optional** real
  Google Gemini provider implements the same interface behind a factory (default
  `fake_local`; gemini opt-in via `LLM_PROVIDER=gemini` + an env key). Mocked
  tests verify SDK→`LlmResponse` mapping (actual usage tokens when present),
  malformed/empty handling, non-negative token/cost, and that the API key never
  appears in the request/metadata. The live smoke is **gated** (`RUN_GEMINI_LIVE=1`)
  and was **not run** here (no key); it skips cleanly by default.
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

**Stage 11 status:** a Gmail JSON report sender is implemented with a **dry-run
default** and **live-gated** sending (`gmail/`, `tests/unit/gmail/`). Tests pass
with no credentials and make no network call; the live send was not run.

- **AC-MAIL-1** (R-032) — ✅ test-covered: the email body is **exactly**
  `json.dumps(report, ensure_ascii=False, indent=2)` — no greeting/signature/
  markdown/free text; a test decodes the raw message and asserts the body
  **parses back to the original report object**.
- **AC-MAIL-2** (R-037) — ◑ partially (dry-run + mocked): sending uses the Gmail
  API client libraries; the **dry-run** path validates/builds without calling the
  API, and a **mocked** live sender maps a success response to `gmail_message_id`.
  Live sending is opt-in (`RUN_GMAIL_LIVE=1`) and was **not run** here.
- **AC-MAIL-3** (R-036) — ✅ test-covered: OAuth credential/token paths come from
  env vars pointing outside the repo; config does not require the files at
  import/load; the loader/result never include secret content.
- **AC-MAIL-4** (R-036, R-037) — ✅ test-covered (Stage 13B): `gmail.preflight`
  confirms the external OAuth files **exist outside the repo** by path/stat only —
  it never opens or prints their contents and reports `status: ready` with
  `live_send_enabled=false` unless `RUN_GMAIL_LIVE=1`. The manual OAuth smoke
  (Gmail draft + Calendar event) succeeded externally; **no live report send was
  performed** in this stage and no OAuth file was copied into the repo.

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

## 11. Run hardening (Stage 12)

- **AC-HARD-1** (R-068) — ✅ test-covered: a run has a **deterministic** identity —
  the same config + seed yields the same `run_id` and config fingerprint; a config
  change changes the fingerprint (timestamp/git are injectable for tests).
- **AC-HARD-2** — ✅ test-covered: each run has a **JSON-serializable manifest**
  listing enabled vs disabled (not-yet) capabilities and gate/scan status, and the
  manifest contains **no token-like content**.
- **AC-HARD-3** — ✅ test-covered: **failures are classified** into a fixed set of
  categories without leaking secrets; **retries/timeouts** are validated and
  bounded (config-driven, injectable sleep).
- **AC-HARD-4** — ✅ test-covered: **aggregate validation** rejects wrong sub-game
  count, totals mismatch, invalid sub-games, missing winner/outcome/status fields,
  token-like content, and non-local URLs when cloud_status is not local.
- **AC-HARD-5** — ✅ verified: `run_hardened_smoke` runs the fake-local full game,
  builds + validates the official report, builds a manifest, and gates the
  programmatic checks (report_valid, totals_valid, no_secret_like_content,
  json_serializable, local_mcp_verified, gmail_body_json_only) — exit 0.

---

### Pass/fail discipline

A delivery area is "accepted" only when **all** its criteria pass with captured
evidence. Partial passes are recorded as `In progress` in the Requirements Matrix,
never rounded up to `Done`.
