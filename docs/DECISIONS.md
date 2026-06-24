# DECISIONS — Architecture Decision Records

Lightweight ADRs. Status: Accepted unless noted.

## ADR-0001 — Ubuntu terminal + Claude Code workflow
**Context:** Need a reproducible, scriptable dev environment for an AI-assisted
build. **Decision:** Develop on an Ubuntu terminal driven by the Claude Code
workflow. **Consequences:** All steps expressible as shell commands; easy to
document and reproduce; aligns with the course's vibe-coding approach.

## ADR-0002 — uv as the only package manager
**Context:** Multiple Python tooling options exist. **Decision:** Use **uv**
exclusively; forbid pip, `python -m`, requirements.txt, virtualenv, and venv.
**Consequences:** Single lockfile and managed environment; consistent installs
(`uv sync`) and execution (`uv run`); simpler reviewer reproduction.

## ADR-0003 — HTTP for MCP communication from the beginning
**Context:** MCP supports multiple transports; inter-group play needs a network
boundary. **Decision:** Use **HTTP transport** for all MCP communication from
day one, with token auth. **Consequences:** Inter-group play works without
re-architecting; clear auth boundary; slightly more setup than stdio.

## ADR-0004 — Separate official group code from technical slug
**Context:** The official identifier `MaRs-777` is not a clean package name.
**Decision:** Keep **`MaRs-777`** as the official group code and **`mars777`**
as the technical slug (package/module name). **Consequences:** Valid Python
identifiers; both values stored in `constants.py` and config as single truth.

## ADR-0005 — Bonus treated as mandatory scope, implemented after baseline
**Context:** Inter-group play is a bonus but affects architecture. **Decision:**
Treat inter-group play as **mandatory for architecture/planning**, but implement
it only **after a stable baseline** (engine + MCP + agents working in-group).
**Consequences:** HTTP/token boundary designed up front (see ADR-0003); avoids
late rework while not blocking the core path.

## ADR-0006 — Google OAuth credentials kept outside Git
**Context:** The report sender uses Google/Gmail OAuth. **Decision:** Never
commit `credentials.json`, `token.json`, or any OAuth artifact; reference them
via env vars and `.env`; provide placeholders in `.env-example`. **Consequences:**
No secret leakage; clear revoke story in `SECURITY.md`; CI/tests never need
credentials.

## ADR-0007 — Requirements Matrix as the audit backbone
**Context:** The assignment is graded strictly against professional practice, and
prior feedback flagged weak, unevidenced requirement tracking. **Decision:**
Maintain `docs/REQUIREMENTS_MATRIX.md` as the single audit backbone — every
requirement carries an ID, source, priority, planned response, proof artifact,
validation method, risk, and status. **Consequences:** Acceptance criteria and
the risk register reference matrix IDs one-to-one; reviewers can trace any
requirement to its evidence; "Status" is the only volatile column.

## ADR-0008 — Bonus treated as architecture-mandatory scope
**Context:** Inter-group play is officially a bonus but reshapes the network/auth
boundary if added late. **Decision:** Treat the bonus as **mandatory for
architecture and planning** (HTTP transport, token auth, config-driven foreign
URLs designed up front), implemented after a stable in-group baseline.
**Consequences:** No late re-architecture; reinforces ADR-0003/ADR-0005; the
bonus report schema is planned alongside the internal report.

## ADR-0009 — Free-language messages plus interpreted-action logs
**Context:** Agents must communicate in free natural language, yet disputes need
an unambiguous record of what actually happened. **Decision:** Agents exchange
**free natural language**; a deterministic interpreter maps each message to a
concrete engine action, and **both** the raw text and the `interpreted_action`
are logged per turn. **Consequences:** Satisfies the NL requirement while keeping
the engine authoritative; transcripts are sufficient to resolve invalid-move
disputes; ambiguous messages are rejected/clarified, never silently defaulted.

## ADR-0010 — Operational inter-group protocol separated from agent language
**Context:** "Protocol" is ambiguous — it could mean a wire format between agents
or coordination between teams. **Decision:** Keep
`docs/INTERGROUP_BONUS_PROTOCOL.md` strictly **operational** (URL/token exchange,
agreed board/origin/turn order, 3+3 role-swapped sub-games, report
reconciliation, token revocation); it imposes **no** hardcoded message protocol
on the agents, which still speak free natural language. **Consequences:** The
bonus is reproducible and fair without compromising the NL requirement;
infrastructure concerns are documented apart from game language.

## ADR-0011 — Evidence-first submission strategy
**Context:** Prior feedback flagged overclaiming and unevidenced claims.
**Decision:** Every quality or capability claim must cite a concrete proof
artifact (results JSON, transcript, validation output, or screenshot for
cloud/GUI evidence); a matrix requirement may only be marked `Done` once its
proof exists and its validation has been run. **Consequences:** No
"production-ready"/"fully implemented" language without evidence; the final gap
audit checks claim→artifact links; partial work stays `In progress`.

## ADR-0012 — Zero-based (row, col) internal coordinates
**Context:** The engine needs one unambiguous internal coordinate convention.
**Decision:** Use **zero-based `(row, col)`** internally, with `north` decreasing
`row`; the eight compass directions map to fixed `(drow, dcol)` deltas.
**Consequences:** Bounds checks are simple `0 <= v < size`; default 5×5 spans
rows/cols `0…4`; any display or inter-group origin agreement is a presentation
concern handled outside the engine (see `INTERGROUP_BONUS_PROTOCOL.md`).

## ADR-0013 — Thief-first default turn order, sourced from config
**Context:** A turn order must be fixed but remain configurable, not hardcoded in
rule logic. **Decision:** Default turn order is **thief, then cop**, read from the
config `turn_order` key; the engine derives whose turn it is from `move_count %
len(turn_order)`. **Consequences:** Order is data, not code; `max_moves` counts
each applied action (move or barrier) as one move; inter-group play can agree a
different order by config without touching the engine.

## ADR-0014 — Illegal actions return structured results, never raise
**Context:** Agents (and later foreign agents) will attempt illegal actions in
normal flow. **Decision:** `apply_action` **never raises** for an illegal action;
it returns an `ActionResult` with `ok=False` and a `RuleViolation`, leaves state
unchanged (no move/turn advance), and includes a log-ready `event` dict.
**Consequences:** The engine is robust to bad input, disputes are reconstructable
from events, and the turn does not advance on a rejected action — keeping the
game deterministic.

## ADR-0015 — Deterministic baseline agents as the local backbone
**Context:** Stage 3 needs autonomous play without LLMs or external services, and
later MCP/NL stages must have a reference to call or mirror. **Decision:**
Implement **deterministic** baseline policies — cop steps toward the thief, thief
steps away — as pure functions of state, with a fixed canonical direction
ordering for tie-breaking and fallback, and **no randomness**. A policy returns
`None` only when the actor has no legal move. **Consequences:** Self-play is fully
reproducible and unit-testable; the runner handles illegal/None policy outputs
with a legal fallback (a fully stuck actor ends the sub-game as a thief survival);
LLM/Q-learning strategies can later replace these policies behind the same
callable contract without touching the engine or runner.

## ADR-0016 — In-memory, report-first local pipeline (no I/O yet)
**Context:** The final pipeline emails a JSON report, but Stage 3 is local-only
and must not overclaim cloud/MCP/Gmail readiness. **Decision:** Build an
**in-memory, `json.dumps`-serializable** report from structured `SubGameResult`
records; write **no files** and send **no email**; mark `mcp_status` as
`not-deployed` and tag the report `stage: local-self-play`. **Consequences:**
The report schema and totals are validated now with zero external dependencies;
file persistence, MCP URLs, cloud deployment, and Gmail sending are added in their
own later stages without reworking the data model.

## ADR-0017 — Observation isolation under partial observability
**Context:** Partial observability is only meaningful if an agent literally cannot
read what it should not see. **Decision:** Build a per-agent `Observation` that
carries only permitted facts (own role/position, board, move counts, locally
visible barriers, cop barrier budget) and computes opponent visibility by
Chebyshev distance against `visibility_radius`; when the opponent is out of range
the observation stores `opponent_position = None` and **never** holds the hidden
coordinate. Policies act on the `Observation`, not on full state.
**Consequences:** Hidden positions cannot leak through the observation object
(proven by tests asserting the hidden coordinate is absent); the engine remains
the only holder of full state and the authority on legality; LLM/MCP agents can
later consume the same observation contract.

## ADR-0018 — Natural-language transcript with separated audit metadata
**Context:** The course requires free natural-language messages and dispute-grade
evidence, but evidence must not become a hidden side channel. **Decision:** Agents
emit **free English** strings (never JSON/numeric protocol) describing qualitative
relative spatial sense; a transcript record stores the message text plus a
separate `audit` block of debug-only facts. The recipient may read only the
`message`; the `audit` block is for human evidence/debugging and is **never**
consumed by the other agent. **Consequences:** Satisfies the free-language
requirement while keeping reconstructable evidence; tests assert audit content
does not appear in the message text and carries no hidden opponent coordinates.

## ADR-0019 — Qualitative spatial language, no exact coordinates by default
**Context:** A visible opponent could be described precisely, but exact
coordinates would weaken the natural-language framing and leak more than intended.
**Decision:** Messages use **qualitative relative directions** (e.g.
"south-east", "right on top of me") and never numeric coordinates; a hidden
opponent yields a "cannot see" message. Any exact-coordinate debug mode would be
an explicitly documented, negotiated future option. **Consequences:** Messages
stay human and free-form; hidden coordinates are structurally impossible to emit
(the sender's observation has none); tests assert messages contain no digits.

## ADR-0020 — FastMCP over HTTP transport for the MCP servers
**Context:** Stage 5 needs local MCP servers that will later expose public,
authenticated URLs for inter-group play (ADR-0003). **Decision:** Use **FastMCP
3.4.2** (added via uv, pinned `fastmcp>=3.4.2,<4`) with **HTTP transport**
(`run(transport="http", host, port, path)`); build servers with a builder
function so `http_app()` / `list_tools()` are testable without binding a socket.
**Consequences:** HTTP is the transport from day one (no stdio-only rework);
servers run locally on separate ports now and can be exposed via public URLs
later; tests assert tool registration without long-running processes. The LLM
lives in the future client, not the server.

## ADR-0021 — Explicit-token argument as local MCP auth (Stage 5)
**Context:** Protected MCP calls must require a token, but request-metadata/OIDC
auth adds complexity not needed for local development. **Decision:** Stage 5 uses
an explicit **`auth_token` tool argument** checked against an environment
variable (`COP_MCP_TOKEN` / `THIEF_MCP_TOKEN`); a mismatch returns a **structured
unauthorized result** (never raises), and the real token is **never logged or
returned** (redacted). This is documented as **local development auth, to be
upgraded** to request-metadata / OIDC for cloud. **Consequences:** Auth is
unit-testable without a network; no secret is committed (env + `.env-example`
placeholders); the upgrade path to cloud auth is explicit and isolated to the
guard.

## ADR-0022 — Role-separated MCP servers with capability isolation
**Context:** The Cop and Thief have different capabilities (only the cop places
barriers) and must be independently addressable. **Decision:** Ship **two
independent server modules/entrypoints** (`cop_server`/`run_cop`,
`thief_server`/`run_thief`); the **thief server does not register the
barrier-placement tool** at all, and both servers return only role-safe
observations (a hidden opponent's position is never exposed). **Consequences:**
Capability isolation is structural (not a runtime check), each role gets its own
URL/port/token, and tests assert the thief server lacks barrier placement and
that observations do not leak hidden coordinates.

## ADR-0023 — Subprocess server pair for real HTTP E2E
**Context:** Stage 5 proved the server modules/tools exist; Stage 6 must prove the
HTTP transport actually works. **Decision:** Start the Cop and Thief servers as
short-lived **subprocesses** on free `127.0.0.1` ports (`subprocess_pair.py`),
inject tokens and ports via the **child process environment** (dummy local values,
never committed), wait for readiness with a **bounded `ping` retry**, and always
**terminate in `finally`** (escalating to kill). **Consequences:** A genuine
client↔server HTTP round-trip is exercised; no long-running servers leak after a
run; the lifecycle helpers are unit-testable (free port, env injection, terminate
with a fake process) and the live path is covered by the integration test.

## ADR-0024 — Deterministic smoke flow reused for HTTP and in-memory
**Context:** The E2E flow logic should be tested fast and deterministically, yet
also exercised over real HTTP. **Decision:** Write one `run_flow(cop_target,
thief_target, ...)` that accepts **either an HTTP URL or an in-process FastMCP
object** (both valid FastMCP client targets), and returns a JSON-serializable
result. Unit tests run it in-memory (fast, no network); `smoke.py` and the
integration test run it over HTTP. **Consequences:** Flow logic is fully covered
without flakiness; the same code proves the real transport; the smoke exits 0 only
when every check passes.

## ADR-0025 — Default-on HTTP integration test, skippable via env
**Context:** Real subprocess/HTTP tests can be unavailable in some sandboxes.
**Decision:** Run the HTTP E2E integration test **by default** (it is reliable and
fast here), but allow skipping with **`RUN_MCP_E2E=0`** for environments that
cannot spawn local subprocesses; keep the standalone `smoke` command for manual
verification. **Consequences:** Coverage and proof come from the default run;
constrained environments degrade gracefully without failing unrelated gates; the
smoke command remains the canonical manual check.

## ADR-0026 — MCP-backed orchestration with the engine as sole authority
**Context:** Stage 7 plays real games where every turn goes through the MCP
servers, but legality/capture/scoring must remain trustworthy. **Decision:** The
**local orchestrator owns authoritative `SubGameState`** and applies every action
through the **engine** (the only authority); the role servers are consulted over
HTTP per turn for `get_observation` → `compose_message` → `propose_action`, and a
proposed action that the engine rejects is **recorded and replaced by a
deterministic legal fallback** (`first_legal_action`). **Consequences:** Servers
(and later LLM agents behind them) cannot corrupt state or cheat; games always
terminate (capture or `max_moves`, or a stuck actor → thief survival); the same
flow runs over HTTP (smoke/integration) and in-memory (fast unit tests).

## ADR-0027 — Explicit local-status fields on the MCP-backed report
**Context:** The report must not be mistaken for a cloud/published or emailed
result. **Decision:** The MCP-backed report carries explicit status fields —
`transport=local_mcp_http`, `mcp_status=local_verified`, local `cop_mcp_url`/
`thief_mcp_url`, `cloud_status=not_deployed`, `email_status=not_sent`, and
`hidden_state_respected` — and **never stores tokens**. **Consequences:** Any
reader (or grader) sees the precise local scope at a glance; the evidence is
honest about what has and has not been done; tokens cannot leak through results
(asserted by tests).

## ADR-0028 — Official report schema derived from the MCP-backed report
**Context:** The final submission needs a stable, email-ready JSON report, but the
Stage 7 MCP-backed report is operational (full events, dynamic URLs).
**Decision:** Define a **stable internal schema** (`reporting/schemas.py`) and a
builder (`build_official_internal_report`) that **transforms** the MCP-backed
report into it — summarising transcripts and replacing raw event arrays with an
`event_count`, adding `report_type`/`schema_version`/`students`/`evidence`/
`validation_status`, and required `sub_game`/`totals` fields. A separate **bonus
schema example** is provided but explicitly claims no real run. **Consequences:**
The report is JSON-only and email-body ready; it is small and reviewable; the
schema is versioned so later cloud/bonus runs reuse it without breaking shape.

## ADR-0029 — Token-safe validation and sanitized, deterministic evidence
**Context:** Reports and committed evidence must never carry secrets, and evidence
must be reviewable and reproducible in Git. **Decision:** Validation runs a
**recursive token scan** (`find_token_like`) rejecting forbidden keys/values
(auth/access/refresh tokens, secret, password, private_key, the MCP token names,
and dummy local tokens), enforces required fields, and allows local URLs **only**
when `cloud_status` is local/not_deployed. The evidence writer **normalizes**
timestamps and URLs to placeholders, drops full event logs (keeping counts and a
≤4-message excerpt), and **refuses to write** if any token-like content survives.
`.gitignore` tracks only `results/evidence/*.example.json`. **Consequences:**
Committed evidence is deterministic (the game is deterministic; volatile fields are
normalized), small, and provably token-free; a report can be safely used as an
email body later.

## ADR-0030 — Provider-agnostic LLM interface, fake_local by default
**Context:** The assignment expects AI-agent orchestration, but tests must stay
deterministic and offline with no API keys. **Decision:** Define a minimal
provider interface (`complete(prompt, *, role, context) -> LlmResponse`) and ship
a deterministic, standard-library **`fake_local`** provider that reasons over the
role-safe observation and emits a natural-language line ending in `ACTION:
<...>`. A real external provider can later implement the same interface behind an
opt-in flag with keys from the environment. **Consequences:** The architecture is
LLM-ready without any external dependency or secret; the full pipeline (prompt →
provider → parse → engine) is exercised deterministically; token/cost accounting
is real (fake rate 0) and ready for a paid provider.

## ADR-0031 — LLM lives on the orchestrator side, never in the MCP servers
**Context:** MCP servers expose tools; the model must not be embedded in them.
**Decision:** The provider/agent runs in the **trusted orchestrator/client**; the
MCP servers stay tool-only and return only the role-safe observation. The agent
receives the observation + message + rules + allowed actions, **never** hidden
opponent coordinates, and the engine remains the sole authority.
**Consequences:** Clean separation (servers stay simple and replaceable); hidden
state cannot leak into prompts (qualitative directions only); a real LLM swaps in
on the client side without touching the servers or the engine.

## ADR-0032 — Safe ACTION-line parser with deterministic fallback
**Context:** Free-text model output must become a legal engine action without
trusting the model. **Decision:** Parse the action from the last `ACTION:` line
(8 directions with hyphen/underscore variants; cop-only `barrier`), reject
stay/malformed with a structured error, convert to an engine `Action`, and — when
parsing fails or the engine rejects the action — **record it and apply a
deterministic legal fallback** (`first_legal_action`). Parse failures and
fallbacks are counted in the report. **Consequences:** A bad or adversarial
response can never corrupt the game; runs always terminate; the report is honest
about how often the model's action was unusable.

## ADR-0033 — Optional Gemini provider via the official google-genai SDK
**Context:** The assignment benefits from a real LLM, but tests must stay
deterministic, offline, and key-free. **Decision:** Add an **opt-in** Gemini
provider (`llm/gemini_provider.py`) using the official **`google-genai`** SDK
(pinned via uv) behind the existing provider interface; a single non-streaming
`generate_content` call with a small `max_output_tokens` and no tool calling.
Actual usage tokens (`usage_metadata`) are reported when present, otherwise the
existing estimator is used (documented fallback). **Consequences:** The
architecture is real-LLM-ready without changing the engine, servers, or parser;
`fake_local` stays the default and grading-safe path; the deprecated
`google-generativeai` package is not used.

## ADR-0034 — Provider factory: env-selected, default fake_local, no import calls
**Context:** Provider selection must be configuration-driven and safe by default.
**Decision:** `create_provider_from_env` returns **`fake_local` by default** and a
Gemini provider **only** when `LLM_PROVIDER=gemini` **and** `GEMINI_API_KEY` (or
`GOOGLE_API_KEY`) is present; a missing key raises a controlled
`LlmConfigError`. The factory makes **no import-time API calls**, reads only env
var *names* from `config/llm.default.json`, and accepts an injectable `env` for
testing. **Consequences:** Misconfiguration fails loudly and safely; no secret is
needed or committed for normal runs; selection is testable without a network.

## ADR-0035 — Live Gemini smoke is gated; no live calls in tests
**Context:** A real-provider smoke proves integration but must not run (or cost
money) by default or in CI. **Decision:** `gemini_prompted_smoke` **skips** (exit
0, no network) unless `RUN_GEMINI_LIVE=1`; if enabled without a key it returns a
controlled failure (exit non-zero); when enabled with a key it runs **one short
bounded sub-game** (3×3, few moves) and never prints the key. Unit tests **mock
the SDK** and never call the network. **Consequences:** Deterministic proof comes
from `fake_local`; the real path is evidence-of-integration, opt-in, and
cost-bounded; the API key never appears in logs, results, or the repo.

## ADR-0036 — Gmail sender: dry-run default, live sending opt-in
**Context:** The report must be sendable by Gmail, but sending must never happen
by accident, in tests, or in CI. **Decision:** The sender **defaults to dry-run**
(validate + build the MIME/raw message, preview metadata, **no API call**); live
sending happens only when `RUN_GMAIL_LIVE=1`, and a first-time OAuth token is
created only when `RUN_GMAIL_AUTH=1`. Missing credentials in live mode returns a
**controlled failure** (exit non-zero); the Gmail service is injectable so unit
tests mock it. **Consequences:** Default validation needs no credentials and makes
no network call; the live path is explicit, gated, and evidence-of-integration;
the API is exercised only when deliberately enabled locally.

## ADR-0037 — JSON-only email body
**Context:** The instructor email body must contain only structured JSON.
**Decision:** The body is **exactly** `json.dumps(report, ensure_ascii=False,
indent=2)` — no greeting, signature, markdown, logs, or any non-JSON text; the
subject may be human-readable. A test decodes the raw message and asserts the body
**parses back to the original report object**. **Consequences:** The email is
machine-parseable and unambiguous; no prose can sneak into the body; the report's
own validation (token-safety, schema) gates what may be sent.

## ADR-0038 — OAuth credentials/token live outside the repo
**Context:** Gmail OAuth uses a client-secrets file and an issued token that must
never be committed. **Decision:** Credential and token **paths come from env
vars** (`GOOGLE_OAUTH_CLIENT_SECRETS`, `GOOGLE_OAUTH_TOKEN_PATH`) pointing
**outside the repo**; the minimal `gmail.send` scope is used; `.gitignore` blocks
`credentials.json`/`token.json`/`client_secret*.json`; the loader never logs or
returns secret content and `SendResult` carries no secrets. **Consequences:** No
secret is committed or required for tests; if earlier credentials used a broader
scope, the token may need regenerating outside the repo; the revoke story in
`SECURITY.md` applies.

## ADR-0039 — Deterministic run identity and config fingerprint
**Context:** Runs must be reproducible and auditable, but timestamps and git state
are inherently variable. **Decision:** Derive `run_id` only from
`group_slug-stage-config_hash-seed` (no timestamp), where `config_hash` is a
stable SHA-256 over the canonical (sorted) config; the `created_at_utc` and
`git_commit` are **separate metadata that are injectable**, so tests are fully
deterministic while real runs still capture wall-clock/commit. **Consequences:**
The same config + seed always yields the same `run_id` and fingerprint; a config
change changes the fingerprint; identity carries no secrets.

## ADR-0040 — Run manifest with capability flags and scan status
**Context:** A grader/auditor needs to see, per run, exactly what was exercised
and what was deliberately not. **Decision:** Emit a JSON manifest with the run
identity, a config summary, **capabilities_enabled** vs **capabilities_disabled**
(cloud/public URLs, live Gmail, real inter-group all off), the validation gates
run, artifact paths, and `secret_scan_status`/`overclaim_scan_status`. A
token-scan (`scan_manifest_secrets`) verifies the manifest is secret-free,
**exempting only the scan-status meta field names** (which contain the word
"secret"/"overclaim" by design, not secret values). **Consequences:** Each run is
self-describing and honest about scope; the manifest cannot carry tokens; the
no-secret check has no false positive on its own meta fields.

## ADR-0041 — Classified failures and controlled retries/timeouts
**Context:** Failures must be surfaced (not hidden) without leaking secrets, and
timeouts/retries must be bounded and configurable. **Decision:** Define 12
**failure categories** and a classifier that maps exceptions by **type then
name** (never by inspecting a possibly-sensitive message), with dummy-token
redaction for any recorded message. Retry/timeout bounds come from
`config/runtime.default.json` via a validated `RetryPolicy`; `retry_call` takes an
**injectable sleep** so tests stay fast and a resource-guard model validates
request/concurrency/output limits. **Consequences:** Runs fail loudly and
categorically; no secret leaks into a status; retries are bounded and
config-driven, not hardcoded; tests are fast and deterministic.
