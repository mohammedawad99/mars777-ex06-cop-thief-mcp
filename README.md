# Assignment 6 — Dual AI Agent Cop-and-Thief via MCP

**Group code:** `MaRs-777` &nbsp;|&nbsp; **Technical slug:** `mars777`

A two-agent Cop-and-Thief game where each player is driven by an independent AI
agent. Agents communicate with the game through **MCP servers over HTTP**, using
a natural-language protocol, and the final results are reported via a Google
(Gmail) report sender. Inter-group play is treated as in-scope (see
`docs/PRD_bonus_intergroup.md`).

## Status — Stage 15F (final bonus_game report sent live to the lecturer)

**The final agreed `bonus_game` report was emailed to the lecturer.** Partner group
`orcai-mj` independently recomputed the `result_hash` using the documented method (sha256
over `official_rules` + `sub_games` + `totals_by_group`, sorted-keys compact JSON) and it
**matched** `a0fdf72d…72ac68`; both groups agreed to send the same `bonus_game` report.

```bash
# Send exactly one live bonus_game email to the lecturer (opt-in; idempotent):
RUN_GMAIL_LIVE=1 \
GOOGLE_OAUTH_CLIENT_SECRETS=$HOME/private/google-oauth-mars777/credentials.json \
GOOGLE_OAUTH_TOKEN_PATH=$HOME/private/google-oauth-mars777/token.json \
uv run python scripts/bonus_send_final_email.py
```

One Gmail message was sent to `rmisegal+uoh26b@gmail.com` with a **JSON-only** body — the
agreed `bonus_game` report (`mutual_agreement: true`, `partner_confirmation_status:
confirmed`) with the top-level `result_hash` attached — and a message id was returned:
**`live_gmail_sent: true`, `bonus_email_sent: true`, `internal_game_sent: false`**. The body
is ID-redacted (no national IDs reach Gmail), OAuth files stay outside the repo, and the
sanitized evidence (`results/evidence/bonus_game_email_sent.example.json`) records only safe
flags + hash + totals (`token_values_recorded: false`, `oauth_contents_recorded: false`). An
idempotency guard refuses a second send, so **no duplicate email** is possible. **No
`internal_game` email was sent in this stage.**

## Status — Stage 15E (mutual agreement finalized + bonus_game Gmail draft preview)

**The official inter-group bonus game is completed and mutually agreed.** Partner group
`orcai-mj` reviewed the canonical result and **confirmed in writing** that it is identical
and correct (totals orcai-mj 90 / MaRs-777 30; Set A thief survived 25 moves ×3; Set B cop
captured at move 14 ×3) and that the official rules and their agent transcript matched,
explicitly approving `mutual_agreement=true`. The canonical `bonus_game` report is finalized
to `mutual_agreement: true`, `partner_confirmation_status: confirmed`, `bonus_claim: true` —
**without changing any winner, move count, total, rule, or transcript**.

```bash
# Finalize agreement + create a Gmail DRAFT preview (never sends):
GOOGLE_OAUTH_CLIENT_SECRETS=$HOME/private/google-oauth-mars777/credentials.json \
GOOGLE_OAUTH_TOKEN_PATH=$HOME/private/google-oauth-mars777/token.json \
uv run python scripts/bonus_finalize_agreement.py
```

The `result_hash` is **unchanged** (`a0fdf72d…72ac68`) — it is computed over outcome fields
only — and the final handoff/evidence ship a **derived** `hash_method` (sha256; canonical
`json.dumps(core, sort_keys=True, separators=(",", ":"))`; exact included/excluded fields;
a 3-step recompute recipe) so the partner can reproduce the digest independently. Final
token-free, ID-redacted artifacts: `results/evidence/bonus_game_report_final_agreed.example.json`,
`bonus_game_partner_handoff_final.example.json`, `bonus_game_mutual_agreement.example.json`.

A **Gmail draft/preview was prepared only**: a JSON-only bonus_game draft to the lecturer
(`rmisegal+uoh26b@…`) was created in Gmail (`gmail_draft_created: true`) and **never sent**
(`RUN_GMAIL_LIVE` unset; `live_gmail_sent: false`, `bonus_email_sent: false`). The draft body
is the ID-redacted report, so no national ID reaches Gmail. **The live email has not been
sent yet.**

## Status — Stage 15D (official inter-group bonus game played)

**The official inter-group bonus game against partner group `orcai-mj` was played**
over the live MCP endpoints, fully autonomously — an automated **referee** (not a human)
chooses every move. Our `GameEngine` stays the single canonical authority for the agreed
rules (8x8, thief-first, 6 sub-games, ≤25 moves, ≤5 cop-only barriers, diagonal, 0-based
`[row, col]`). One role is our deployed Cloud Run server (our contract); the other is the
partner's server (their `setup`/`observe`/`my_move`/`state` contract) — our moves are
mirrored to the partner via `observe`, theirs come from `my_move`.

```bash
# Official bonus game (tokens from the git-ignored files; no Gmail, no human moves):
set -a; . .secrets/cloud-run.local.env; set +a
uv run python scripts/run_bonus_game.py
```

Both pairing directions ran — Set A (3) MaRs-777 Cop vs orcai-mj Thief, Set B (3)
orcai-mj Cop vs MaRs-777 Thief. Result (deterministic, **6/6 decided on 8x8**): Set A →
orcai-mj thief survived 25 moves ×3; Set B → orcai-mj cop captured at move 14 ×3.
**totals_by_group: MaRs-777 30 / orcai-mj 90** (orcai-mj 6 wins). Canonical `bonus_game`
JSON, a token-free partner handoff with `result_hash a0fdf72d…72ac68`, and sanitized run
evidence are written under `results/evidence/bonus_game_*` (no tokens; **all student
national IDs redacted for both groups**); `validation_status: valid`.

**Honest note:** our deployed servers were provisioned for the 5x5 visibility config, so
our agents play weaker on the official 8x8 board (far-edge moves defer to the engine's
documented legal fallback). This is the real, autonomous outcome — not faked. **No Gmail
was sent, the bonus report was not sent, and `mutual_agreement` stays `false`
(`partner_confirmation_status: pending`)** until the partner confirms the `result_hash`
matches.

## Status — Stage 15C (live partner compatibility smoke + adapter reconciliation)

**Live compatibility against the partner group (`orcai-mj`) was verified and passed**,
and our partner adapter was reconciled to their **real** MCP contract. The partner's
INTEROP doc was still not public, so the live tool schemas were inspected directly —
the Stage 15B provisional payloads were wrong on every tool. Confirmed contract: token
key `token`; `setup(cop, thief, rows, cols, origin, max_moves, max_barriers, diagonal,
token)` with 0-based `cop`/`thief` **start positions** → `{role, snapshot}`;
`observe(message, mover, token)` (opponent-move notice); `my_move(token)` (the partner
makes **its own** move); `state(token)`.

```bash
# Live partner compatibility smoke (partner URLs/tokens from the git-ignored file):
uv run python scripts/bonus_partner_live_smoke.py
```

Result (`results/evidence/bonus_partner_live_smoke.example.json`):
`partner_smoke_passed: true` — unauthorized rejected, authorized accepted,
setup/observe/my_move/state OK, **role identity** consistent per server (cop→`cop`,
thief→`thief`), 0-based `[row,col]` accepted, **thief-first** accepted, and **both 5x5
and 8x8** warm-ups pass. Official board size **recommendation: 5x5** (our baseline) —
**not frozen** (mutual agreement pending). **No official bonus game was run, no Gmail
was sent, and no partner token/student ID was printed or committed** (evidence carries
presence booleans only; `tokens_recorded: false`).

## Status — Stage 14A (public-cloud full game + final report dry-run)

**A complete 6-sub-game game was played over the deployed public Cloud Run URLs**,
and the **official internal report** was generated, schema-validated, and run
through the Gmail sender in **dry-run only** (no email sent). Result: 6/6 sub-games
decided (totals cop 30 / thief 60), `report_schema_valid: true`, bad token rejected
over the public URL, `gmail_dry_run_status: dry_run` with `body_json_valid: true`.

```bash
# Full public-cloud game + official report dry-run (tokens from the ignored file):
set -a; . .secrets/cloud-run.local.env; set +a
uv run python scripts/public_cloud_final_dry_run.py
```

The official report carries `group_code: MaRs-777`, students, the real
`github_repo`, the public `cop_mcp_url`/`thief_mcp_url` (`…/mcp`), timezone,
6 `sub_games`, and `totals`, with `cloud_status: deployed`. Sanitized, token-free
evidence: `results/evidence/public_cloud_full_game.example.json` (the full report)
and `results/evidence/final_report_dry_run.example.json` (summary). **No live Gmail
was sent, no inter-group bonus game was played, and the final submission is not
complete** — those remain later steps. Tokens stayed only in git-ignored `.secrets/`.

**Student privacy (Stage 14B):** student national-IDs are **not** stored in any
tracked file. The report script loads the real identities at runtime from a local
git-ignored file (`MARS777_STUDENTS_FILE`, default `.secrets/students.local.json`)
for the in-memory report and Gmail dry-run; tracked evidence **redacts** the IDs
(`id: REDACTED`) and records `identity_privacy` flags. A brief earlier commit had
exposed the IDs, so a **public-history scrub** was performed (`git filter-repo`
replacing the IDs with `REDACTED_STUDENT_ID`, then `git push --force-with-lease`);
**all reachable Git history is now ID-free** (verified in a fresh clone). The real
identities live only in the local git-ignored `.secrets/students.local.json`.

**Gmail draft preview (Stage 14C):** a Gmail **draft** (never sent) of the official
JSON report was created to the student's **own** account (not the lecturer) — subject
`PREVIEW ONLY - …`, JSON-only schema-valid body (`scripts/gmail_draft_preview.py`).
It is a preview, **not** the official submission; the live send to the lecturer and
the inter-group bonus are still pending.

## Status — Stage 13C (live Cloud Run deployment)

**Both MCP services are deployed and live on Google Cloud Run** in project
`api-mars-777`, region `me-west1`:

| Role | Service | Public URL | MCP endpoint |
|------|---------|------------|--------------|
| Cop | `mars777-cop-mcp` | `https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app` | `…/mcp` |
| Thief | `mars777-thief-mcp` | `https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app` | `…/mcp` |

**Auth boundary:** Cloud Run IAM allows unauthenticated requests **only because the
MCP app itself enforces a per-service token** on protected tools (the `auth_token`
argument). A wrong/absent token returns a structured `unauthorized` result; the
correct token is accepted. Public smoke against both live URLs passes — unauthorized
rejected, authorized healthy, role-correct, hidden opponent not leaked, thief
exposes no barrier tool. Tokens were generated locally with Python `secrets`, stored
only in git-ignored `.secrets/`, and are **never printed or committed**.

```bash
# Reproduce the public smoke (tokens sourced from the local ignored env file):
set -a; . .secrets/cloud-run.local.env; set +a
COP_MCP_URL=https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app \
THIEF_MCP_URL=https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app \
uv run python scripts/public_cloud_smoke.py
```

Sanitized deployment evidence (no tokens): `results/evidence/cloud_deployment.example.json`.
**No live Gmail report has been sent, no real inter-group bonus game has been
played, and the final submission is not complete** — those remain later steps.

## Status — Stage 13B (live-readiness preflight)

**A live-readiness preflight is implemented** — a safe bridge from the local
implementation to live operations. It combines a Gmail OAuth external-file check,
read-only Cloud Run / `gcloud` checks, and the existing packaging preflight into
one JSON report that makes every remaining blocker explicit. **It deploys nothing
and sends no live Gmail**: it only inspects existence, location, and read-only
state, then lists the exact manual actions left before a live deploy or live send.

```bash
uv run python -m mars777_cop_thief.deployment.live_readiness
```

The Gmail check reads only the *paths* in `GOOGLE_OAUTH_CLIENT_SECRETS` /
`GOOGLE_OAUTH_TOKEN_PATH`, confirms the files exist **outside** the repo, and
**never opens their contents**; `live_send_enabled` stays `false` unless
`RUN_GMAIL_LIVE=1`. The cloud check uses only read-only commands (`gcloud version`,
active account/project, best-effort billing) — it never runs deploy/build/enable
and reports missing gcloud, no auth, project mismatch, or unknown billing as
**blockers/warnings, not crashes**. The command exits `0` whenever the checks
complete, even when blockers remain. **No live Gmail send and no cloud deployment
occur**, and no credential/token contents appear in the output. The expected
project is `api-mars-777`; the recommended region is `me-west1` (override with
`CLOUD_RUN_REGION`).

## Status — Stage 13A (cloud deployment packaging & preflight)

**Cloud deployment packaging and preflight are implemented** for two independent
MCP services (`mars777-cop-mcp`, `mars777-thief-mcp`) — **no live deployment was
performed and no public URL exists yet**. A single role-aware container
(`Dockerfile` + `mcp_servers/cloud_entrypoint.py`) runs either the Cop or Thief
server, selected by `MCP_ROLE` (`cop`/`thief`); in cloud mode it binds `0.0.0.0`
and reads `PORT`, while local mode keeps `127.0.0.1`. The role's token comes from
the runtime environment / secret manager — **never baked into the image, logged,
or committed**.

Run the deployment preflight (validates packaging readiness; no cloud calls, no
gcloud, no credentials):

```bash
uv run python -m mars777_cop_thief.deployment.preflight
```

It checks `config/cloud.default.json`, the `Dockerfile`/`.dockerignore`, that no
secret files are present, that `cloud_status` is `not_deployed` with placeholder
public URLs, and that `MCP_ROLE`/`PORT` resolve without starting a server. The
target platform is **Google Cloud Run** (documented in `docs/CLOUD_DEPLOYMENT.md`;
any HTTPS container platform works). Live deploy is a **separate, manual, gated
step** (`RUN_CLOUD_DEPLOY=1`) — see the guide; `scripts/cloud_run_deploy_template.sh`
is an inert placeholder template.

This stage is still local-only: **no Cloud Run service has been created**, **no
public URL has been deployed**, **no live Gmail email was sent**, and **no real
inter-group bonus game** has been completed.

## Status — Stage 12 (hardened run validation, manifest & reproducibility)

A **run-hardening layer** is implemented (`src/mars777_cop_thief/run/`): a
deterministic run identity (`run_id` from group/stage/config-hash/seed, with
injectable timestamp/git for reproducible tests), a JSON-serializable **run
manifest** (capabilities enabled/disabled, validation gates, scan status), a
structured **failure classification** (12 categories) with secret-safe
redaction, a validated **retry/timeout policy** + resource guard
(`config/runtime.default.json`), and **aggregate validation** of a full report
(exact sub-game count, totals match, no invalid sub-games, winners/outcomes
present, required status fields, no token-like content, local URLs only when
local).

Run the hardened local smoke — it runs the fake-local prompted MCP full game,
builds the official report, validates it as a whole, builds a manifest, and gates
programmatic quality checks (report_valid, totals_valid, no_secret_like_content,
json_serializable, local_mcp_verified, gmail_body_json_only):

```bash
uv run python -m mars777_cop_thief.run.hardened_smoke
```

Manifests and results carry **no tokens/secrets**. This stage remains local-only:
**no cloud/public URLs**, **no live Gmail send**, **live Gemini only if enabled by
the existing gate**, and **no real inter-group bonus game** has been completed.

## Status — Stage 11 (Gmail JSON report sender, dry-run + live-gated)

A **Gmail JSON report sender** is implemented with a **dry-run** default and
**live-gated** sending (`src/mars777_cop_thief/gmail/`, official Google API
client libraries). The email **body is the JSON report only** — exactly
`json.dumps(report, ensure_ascii=False, indent=2)`, with no greeting, signature,
markdown, or any non-JSON text (proven by a parse-back test). The subject is
human-readable; the default recipient is `rmisegal+uoh26b@gmail.com`
(configurable via `GMAIL_REPORT_RECIPIENT`).

**Live sending is opt-in.** By default the CLI runs a dry-run (validates, builds
the MIME/raw message, previews send metadata) **without calling Gmail**:

```bash
uv run python -m mars777_cop_thief.gmail.send_report   # dry-run, exit 0
```

Live sending requires `RUN_GMAIL_LIVE=1` **and** OAuth desktop credentials/token
files stored **outside the repo** (`GOOGLE_OAUTH_CLIENT_SECRETS` /
`GOOGLE_OAUTH_TOKEN_PATH`); a first-time token is created only with
`RUN_GMAIL_AUTH=1`. The minimal `gmail.send` scope is used. **No credential or
token is committed or required for tests**, and the key/token never appears in
logs, headers, the report, or the result. Normal validation passes with no
credentials.

This stage remains local-only: **no cloud/public URLs** and **no real
inter-group bonus game** has been completed; a **live Gmail email was not sent**
here (`RUN_GMAIL_LIVE` not enabled).

## Status — Stage 10 (optional Google Gemini provider, live-gated)

An **optional real Google Gemini provider adapter** is implemented behind the
existing LLM provider interface (`llm/gemini_provider.py`, official `google-genai`
SDK). It is **opt-in**: the default provider stays `fake_local`, and **normal
validation and all tests pass with no API key**. A provider factory
(`create_provider_from_env`) returns `fake_local` unless `LLM_PROVIDER=gemini`
with `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) present; a missing key raises a
controlled error. The key is read from the environment only and is **never
logged, returned, or placed in metadata**; hidden opponent coordinates are never
sent in prompts.

`fake_local` remains the **deterministic, grading-safe mode** (use
`prompted_game_smoke` for reproducible proof). The real Gemini path has a
**live-gated smoke**: by default it skips (exit 0, no network); it runs a single
short bounded sub-game only when explicitly enabled:

```bash
# Skips cleanly by default (no key, no network):
uv run python -m mars777_cop_thief.mcp_client.gemini_prompted_smoke

# Live (local only): requires RUN_GEMINI_LIVE=1 and a key set in your environment
RUN_GEMINI_LIVE=1 GEMINI_API_KEY=... uv run python -m mars777_cop_thief.mcp_client.gemini_prompted_smoke
```

**No API key is committed or required for tests.** This stage is still
local-only: **no cloud/public URLs**, **no Gmail/email sending**, and **no real
inter-group bonus game** has been completed.

## Status — Stage 9 (prompted MCP agent layer, offline fake LLM)

A **provider-agnostic LLM-agent layer** and a **prompted MCP-backed game** are
implemented and pass. The provider lives on the orchestrator side (never in the
MCP servers): a deterministic, offline **`fake_local`** provider reasons over the
role-safe observation and emits a natural-language line ending in
`ACTION: move <direction>`; a parser extracts the action; an invalid/illegal
action is recorded and replaced by a deterministic legal fallback. The engine
remains the only authority for legality/capture/scoring.

Each turn the orchestrator calls `get_observation`/`compose_message` over MCP,
builds a role-specific prompt (no hidden opponent coordinates, no tokens/secrets),
calls the provider, parses the action, and applies it. The JSON report adds
`llm_mode: fake_local`, `provider_name`, `model_name`, token estimates,
`estimated_cost_usd`, `parse_failures`, and `fallbacks_used`.

Run the prompted MCP game smoke (offline fake provider over real HTTP):

```bash
uv run python -m mars777_cop_thief.mcp_client.prompted_game_smoke
```

**No external LLM API is implemented** (no OpenAI/Gemini/Anthropic calls, no API
keys) — only the offline `fake_local` provider. This stage is still local-only:
**cloud/public URLs are not deployed**, **Gmail/email sending is not
implemented**, and **no real inter-group bonus game has been completed**.

## Status — Stage 8 (official report schema, validation & evidence pack)

The **official report schema, validation, and a local evidence pack are
implemented** and pass. A stable internal report schema
(`src/mars777_cop_thief/reporting/`) is built from the Stage 7 MCP-backed report,
**validated** (required fields, token-safety, local-URL rule), and is
JSON-only — ready to be an email body later. A **bonus/inter-group schema
example** exists too, but it explicitly makes **no claim that a real inter-group
game has been run** (`bonus_claim: false`, `mutual_agreement: false`).

The reports are **token-safe**: validation rejects any key/value that looks like
`auth_token`, `access_token`, `refresh_token`, `secret`, `password`,
`private_key`, `COP_MCP_TOKEN`/`THIEF_MCP_TOKEN`, or a dummy local token; the
report omits all tokens.

Generate the sanitized, deterministic evidence pack (committed under
`results/evidence/` as `*.example.json` — normalized URLs/timestamp, no tokens,
no full event logs):

```bash
uv run python -m mars777_cop_thief.reporting.generate_evidence_pack
```

This stage is still **local-only**: **Gmail/email sending is not implemented**,
**cloud/public URLs are not deployed**, and the **bonus schema exists but no real
inter-group bonus game has been completed**.

## Status — Stage 7 (MCP-backed local game orchestration)

The **local MCP-backed game orchestration is implemented and passes**: a trusted
orchestrator (`src/mars777_cop_thief/mcp_client/game_flow.py`) plays real
sub-games where **every turn calls the Cop/Thief MCP servers over HTTP** —
`get_observation` → `compose_message` → `propose_action` — then applies the
proposed action through the local game engine (the only authority for legality,
capture, and scoring). The full default game (6 sub-games) runs end-to-end over
HTTP.

The MCP-backed report is JSON-serializable and states **local** status only:
`transport=local_mcp_http`, `mcp_status=local_verified`, local `cop_mcp_url` /
`thief_mcp_url`, `cloud_status=not_deployed`, `email_status=not_sent`, plus
`hidden_state_respected`. The orchestrator may send full state to
`get_observation`, but the server returns only the role-safe filtered observation
and `propose_action` consumes only that — hidden opponent coordinates never leak.

Run the MCP-backed game smoke (starts both servers, plays the full game over
HTTP, prints JSON, exits 0 on pass):

```bash
uv run python -m mars777_cop_thief.mcp_client.game_smoke
```

A real-HTTP one-sub-game integration test runs by default
(`tests/integration/mcp/test_http_game_e2e.py`; skip with `RUN_MCP_E2E=0`). This
stage is still **local-only**: **no public URLs / cloud deployment**, **no
Gmail/email sending**, **no external-LLM calls**, **no GUI**, and **no
inter-group remote play** — those remain later stages.

## Status — Stage 6 (local MCP client & HTTP E2E smoke)

The **local MCP HTTP end-to-end smoke is implemented and passes**: a client
(`src/mars777_cop_thief/mcp_client/`) starts the Cop and Thief servers as local
subprocesses on free `127.0.0.1` ports, connects over **HTTP** with the official
FastMCP `Client`, and drives a deterministic flow — proving the transport works
end-to-end, not just that the tool modules exist.

The smoke verifies, over real HTTP, for **both** roles: `health_check`,
`get_role_info`, valid-token `get_observation`/`compose_message`/`propose_action`,
a wrong-token call returning a structured **unauthorized** result, that a hidden
opponent's position stays `None` (no leak), that messages are plain text, that
actions are structured, and that the **Thief server exposes no barrier tool**.
Servers are always torn down afterward.

Run the local E2E smoke (starts both servers, prints a JSON result, exits 0 on
pass):

```bash
uv run python -m mars777_cop_thief.mcp_client.smoke
```

The real HTTP E2E also runs as a pytest integration test by default
(`tests/integration/mcp/`); set `RUN_MCP_E2E=0` to skip it where local
subprocesses are not allowed. This stage is still **local-only**: **no public
URLs / cloud deployment**, **no Gmail/email sending**, **no external-LLM calls**,
**no GUI**, and **no inter-group remote play**.

## Status — Stage 5 (local HTTP MCP servers)

The **local HTTP MCP server layer is implemented** and unit-tested: two
independent FastMCP servers (Cop and Thief) that expose role-safe tools
delegating to the existing engine / observability / dialogue / policy code
(`src/mars777_cop_thief/mcp_servers/`, exercised by `tests/unit/mcp_servers/`).
The LLM does **not** live in the servers — they only expose tools/resources for a
future client/orchestrator to call.

- Tools (both roles): `get_role_info`, `health_check`, `get_observation`
  (role-safe; hidden opponent never leaked), `compose_message` (free text),
  `propose_action` (observation-based policy). **Cop-only:**
  `place_barrier_candidate`. The **Thief server does not expose barrier
  placement**.
- Transport is **HTTP** (FastMCP `transport="http"`), runnable locally on
  separate ports (Cop `8001`, Thief `8002`) — config in
  `config/mcp.local.default.json`.
- Protected tool calls require a token via an explicit `auth_token` argument
  checked against an environment variable (`COP_MCP_TOKEN` / `THIEF_MCP_TOKEN`).
  This is **local development auth**, to be upgraded for cloud. The real token is
  never logged or returned.

This stage is **local-only**: there are **no public URLs and no cloud deployment
yet**, **no Gmail/email sending**, **no external-LLM calls**, **no GUI**, and **no
inter-group remote play**. Those remain later stages (see `docs/TODO.md`).

Run the local MCP servers (each in its own terminal, after setting tokens in
`.env`):

```bash
uv run python -m mars777_cop_thief.mcp_servers.run_cop     # Cop server  → 127.0.0.1:8001/mcp
uv run python -m mars777_cop_thief.mcp_servers.run_thief   # Thief server → 127.0.0.1:8002/mcp
```

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
  mcp_servers/        local HTTP MCP servers (Cop/Thief), auth guard, tools
  mcp_client/         local MCP client, server-pair lifecycle, E2E + game flow
  llm/                provider interface, fake + optional Gemini provider, factory, prompts, parser, agent
  reporting/          official report schema, validation, evidence pack writer
  gmail/              Gmail JSON report sender (dry-run + live-gated), MIME, auth
  run/                run identity/manifest, failure classes, retry, aggregate validation
results/evidence/     sanitized, deterministic example artifacts (*.example.json)
tests/unit/           version, config, and SDK smoke tests
tests/unit/game/      engine TDD suite (models, rules, engine, events, SDK)
tests/unit/agents/    baseline + observed policy tests
tests/unit/observability/  visibility and observation tests
tests/unit/dialogue/  message and transcript tests
tests/unit/orchestration/  runner, dialogue runner, report, and SDK tests
tests/unit/mcp_servers/    auth, tools, server-builder, run/config tests
tests/unit/mcp_client/     client URLs, lifecycle, in-memory flow, smoke entry
tests/integration/mcp/     real HTTP end-to-end smoke (default-on)
tests/unit/reporting/      schema validation, official report, evidence tests
tests/unit/llm/            provider, prompt, parser, cost, agent tests
tests/unit/gmail/          config, MIME (JSON-only), auth, sender, CLI/SDK tests
tests/unit/run/            identity/manifest, status/retry, validation/smoke tests
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
