# REQUIREMENTS MATRIX — Audit Backbone

**Group:** MaRs-777 (`mars777`) · **Stage:** 1 (Requirements hardening) · **Status:** Baseline established

This matrix is the single audit backbone for the project. Every requirement is
traceable to a source category, a planned response, a concrete proof artifact, a
validation method, and a status. It is updated each stage; "Status" is the only
column expected to change frequently.

## Legend

- **Priority**
  - `Mandatory` — baseline assignment requirement; failure fails the submission.
  - `Strong` — strongly expected professional practice; weak here loses points.
  - `Bonus-Mandatory` — officially a bonus, but treated as mandatory scope here
    (inter-group play) per ADR-0005.
  - `Optional` — creative/extra; must never risk core delivery.
- **Source category**: `Game`, `MCP`, `Protocol`, `Cloud`, `Bonus`, `Report`,
  `Email`, `Security`, `Docs`, `Quality`, `Process`, `Feedback`.
- **Risk level**: `Low` / `Med` / `High` — delivery risk if mishandled.
- **Status**: `Planned` / `In progress` / `Done` / `Blocked`.

## Matrix

| ID | Requirement | Source category | Priority | Planned response | Proof artifact | Validation method | Risk level | Status |
|----|-------------|-----------------|----------|------------------|----------------|-------------------|------------|--------|
| R-001 | Two AI agents exist: one Cop, one Thief, each independent | Game | Mandatory | LLM agent decides each role over MCP; provider-agnostic — offline `fake_local` (default) or optional real Gemini (opt-in); engine authoritative | `llm/agent.py`, `llm/fake_provider.py`, `llm/gemini_provider.py`, `mcp_client/prompted_game_flow.py`, `tests/unit/llm/` | Prompted game: both roles act via agent over HTTP; Gemini opt-in | Med | In progress |
| R-002 | Two MCP servers exist: one for Cop, one for Thief | MCP | Mandatory | Independent FastMCP cop/thief servers run as subprocesses on separate free ports; driven over HTTP | `mcp_servers/*_server.py`, `mcp_client/subprocess_pair.py`, `tests/integration/mcp/test_http_e2e.py` | E2E smoke starts both and calls each over HTTP | Med | In progress |
| R-003 | Communication uses free natural language, not a rigid numeric protocol | Protocol | Mandatory | Local free-text messages (qualitative, no JSON/opcodes/coords); over-MCP exchange later | `dialogue/messages.py`, `dialogue/transcript.py`, `tests/unit/dialogue/` | Tests assert plain-string, no-digit messages | High | In progress |
| R-004 | MCP communication is HTTP-based from the beginning (not stdio-only) | MCP | Mandatory | FastMCP `transport="http"`; real client↔server HTTP round-trip proven (ADR-0020/0023) | `mcp_client/`, `tests/integration/mcp/test_http_e2e.py`, `smoke` command output | E2E smoke passes over HTTP (exit 0) | Med | In progress |
| R-005 | Baseline supports local self-play | Game | Mandatory | Full self-play runs **over MCP/HTTP** each turn (orchestrator + role servers) locally **and over the deployed public Cloud Run `/mcp` URLs** | `mcp_client/game_flow.py`, `mcp_client/game_smoke.py`, `scripts/public_cloud_final_dry_run.py`, `results/evidence/public_cloud_full_game.example.json` | 6-sub-game game passes locally and over public HTTPS (exit 0) | Med | Done |
| R-006 | Submission supports cloud/self-play through public URLs | Cloud | Mandatory | **Deployed** to Cloud Run (`api-mars-777`/`me-west1`): both MCP services live at public URLs; public HTTPS smoke passes (bad token rejected, good token healthy) | `Dockerfile`, `mcp_servers/cloud_entrypoint.py`, `scripts/public_cloud_smoke.py`, `results/evidence/cloud_deployment.example.json`, `docs/CLOUD_DEPLOYMENT.md` | Public smoke `passed: true` over HTTPS; URLs in evidence file | High | Done (deployed) |
| R-007 | Inter-group play with another team is supported | Bonus | Bonus-Mandatory | **Played**: automated cross-group referee ran the official 6-sub-game match vs orcai-mj on 8x8 (both directions, thief-first), our `GameEngine` canonical, agents autonomous; live compat smoke passed first | `scripts/run_bonus_game.py`, `bonus/referee.py`, `bonus/sessions.py`, `bonus/cross_engine.py`, `scripts/bonus_partner_live_smoke.py`, `results/evidence/bonus_game_*` | 6/6 sub-games decided; both directions; `result_hash` reproducible; partner confirmation pending | High | Done (15D, confirmation pending) |
| R-008 | Bonus is treated as mandatory architecture scope | Process | Bonus-Mandatory | Network/auth boundary designed up front | ADR-0005, this matrix | Architecture review | Low | Done |
| R-009 | Each team exposes two URLs: Cop MCP URL and Thief MCP URL | Cloud | Mandatory | **Two live public URLs**: `mars777-cop-mcp` and `mars777-thief-mcp` on Cloud Run, each role-separated with its own token | `results/evidence/cloud_deployment.example.json`, `docs/CLOUD_DEPLOYMENT.md`, `README.md` | Both URLs respond; smoke confirms role-correct + token-gated | Med | Done (deployed) |
| R-010 | URLs are protected by token/auth; no open public endpoint | Security | Mandatory | Protected tools require `auth_token` vs env var (local dev auth, ADR-0021); exercised through the HTTP client path; upgrade to request-metadata for cloud | `mcp_servers/auth.py`, `tests/unit/mcp_servers/test_auth.py`, `tests/integration/mcp/test_http_e2e.py` | Unit + E2E: wrong token → structured unauthorized; token never revealed | High | In progress |
| R-011 | Game is turn-based | Game | Mandatory | Engine advances one actor per turn deterministically | `game/state.py`, `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test alternates turns | Low | Done |
| R-012 | Default board is 5×5 | Game | Mandatory | `grid_size` default `[5,5]` in config | `config/game.default.json` | Config test asserts default | Low | Done |
| R-013 | Game parameters are not hardcoded; read from config | Quality | Mandatory | All params loaded via `shared/config.py` | `config/*.json`, config loader | grep shows no literals in engine | Med | In progress |
| R-014 | Start with small sanity grids 2×2, then 3×3, 4×4, finally 5×5 | Game | Strong | `sanity_grid_sizes` list drives staged tests | `config/game.default.json`, tests | Parametrized tests over all sizes | Low | Done |
| R-015 | Each full game has 6 sub-games | Game | Mandatory | `num_sub_games` default 6 | Config, orchestrator | Run produces 6 sub-game records | Low | Done |
| R-016 | Each sub-game has up to 25 moves | Game | Mandatory | `max_moves` default 25 enforced by engine | `config/game.default.json`, `game/engine.py`, `tests/unit/game/test_engine.py` | Sub-game terminates at `max_moves` | Low | Done |
| R-017 | Cop catches Thief by reaching the same cell | Game | Mandatory | Capture = coordinate equality check | `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test: same cell → capture (both directions) | Low | Done |
| R-018 | Thief wins a sub-game by surviving all moves without capture | Game | Mandatory | Survival-to-`max_moves` → Thief win | `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test: no capture → Thief win | Low | Done |
| R-019 | Movement allows one step in all 8 directions incl. diagonals | Game | Mandatory | 8 compass deltas; one-step Chebyshev validation | `game/models.py`, `game/rules.py`, `tests/unit/game/test_rules.py` | Unit test each direction | Low | Done |
| R-020 | Stay not allowed in baseline unless explicitly negotiated/documented | Game | Mandatory | `allow_stay` default `false`; toggle documented | `config/game.default.json`, `game/rules.py`, `tests/unit/game/test_rules.py` | Engine rejects stay when false | Low | Done |
| R-021 | Cop may place barriers instead of moving | Game | Mandatory | Cop action set includes `place_barrier` | `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test: barrier as a turn | Med | Done |
| R-022 | Cop may place at most 5 barriers per sub-game | Game | Mandatory | `max_barriers` enforced per sub-game | `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test: limit-reached rejected | Low | Done |
| R-023 | Thief cannot place barriers | Game | Mandatory | Engine role guard rejects thief barrier | `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test: thief barrier illegal | Low | Done |
| R-024 | Barriers block both Cop and Thief | Game | Mandatory | Move validation rejects entering a barrier cell | `game/rules.py`, `tests/unit/game/test_rules.py` | Unit test: move into barrier blocked | Low | Done |
| R-025 | Illegal moves are detected and logged | Game | Mandatory | Structured `ActionResult`+`event`; file logging later | `game/engine.py`, `game/events.py`, `tests/unit/game/` | Unit test: illegal action → violation+event | Med | In progress |
| R-026 | Logs are retained for disputes | Process | Mandatory | In-memory per-turn structured events + NL transcript with audit facts; file persistence later | `orchestration/dialogue_runner.py`, `dialogue/transcript.py`, `tests/unit/orchestration/` | Inspect events+transcript after a run | Med | In progress |
| R-027 | Scoring — Cop win: Cop 20, Thief 5 | Game | Mandatory | `scoring.cop_win=20`, `cop_loss/thief_loss=5`; `score_state` | `config/game.default.json`, `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test scoring on cop win | Low | Done |
| R-028 | Scoring — Thief win: Thief 10, Cop 5 | Game | Mandatory | `scoring.thief_win=10`, `cop_loss=5`; `score_state` | `config/game.default.json`, `game/engine.py`, `tests/unit/game/test_engine.py` | Unit test scoring on thief win | Low | Done |
| R-029 | Maximum team score over 6 sub-games is 90 | Game | Strong | 6 × 15-max-per-side invariant; totals aggregator | `orchestration/totals.py`, `tests/unit/orchestration/` | Property test: total ≤ 90 | Low | In progress |
| R-030 | Minimum team score is 30 | Game | Strong | 6 × 5 floor; totals aggregator | `orchestration/totals.py`, `tests/unit/orchestration/` | Property test: total ≥ 30 | Low | In progress |
| R-031 | Final report is JSON | Report | Mandatory | Official internal schema built+validated from the MCP-backed report; JSON-only, token-safe | `reporting/official_report.py`, `reporting/validators.py`, `tests/unit/reporting/` | Schema validation passes; `json.dumps` succeeds | Med | Done |
| R-032 | Email body to instructor contains only structured JSON, no free text | Email | Mandatory | MIME body is exactly `json.dumps(report, ensure_ascii=False, indent=2)`; no greeting/signature/markdown | `gmail/mime_builder.py`, `tests/unit/gmail/test_config_and_mime.py` | Decode raw → body parses back to report; no free text | Med | In progress |
| R-033 | Internal report includes group name/code, students, repo, Cop URL, Thief URL, timezone, sub_games, totals | Report | Mandatory | Official internal schema carries all fields incl. students + cop/thief MCP urls; built from a **real public-cloud 6-sub-game run** with the public `/mcp` URLs and `cloud_status: deployed`; required-field validation | `reporting/official_report.py`, `scripts/public_cloud_final_dry_run.py`, `results/evidence/public_cloud_full_game.example.json` | Required-field check + `validation_status: valid` on the public-cloud report | Med | Done |
| R-034 | Bonus report includes both group names, both repos, four URLs, students, sub_games, totals_by_group, bonus_claim, mutual_agreement | Bonus | Bonus-Mandatory | **Real** canonical `bonus_game` report built from the played match (both groups/repos, four public URLs, pairing-labelled sub_games, totals_by_group, official_rules, `result_hash`); `validate_bonus_game_report` clean | `bonus/bonus_report.py`, `reporting/schemas.py`, `reporting/validators.py`, `results/evidence/bonus_game_report.example.json` | Schema validation + field check; `validation_status: valid`; student IDs redacted | High | Done (15D) |
| R-035 | If two groups disagree, bonus may be rejected | Bonus | Bonus-Mandatory | Partner **confirmed** the canonical result in writing → `mutual_agreement: true`, `partner_confirmation_status: confirmed` (`bonus/finalize.py`); validator still **rejects** a premature `true`; final handoff ships a **derived** `hash_method` so the partner can reproduce `result_hash` (unchanged `a0fdf72d…`) | `bonus/finalize.py`, `bonus/bonus_handoff.py`, `reporting/validators.py`, `results/evidence/bonus_game_*_final*.json`, `results/evidence/bonus_game_mutual_agreement.example.json`, `tests/unit/bonus/` | Agreement finalized; hash unchanged + reproducible from documented recipe (tested) | Med | Done (15E) |
| R-036 | Google OAuth credentials and token stay outside Git | Security | Mandatory | `.gitignore` excludes OAuth files; env refs | `.gitignore`, `.env-example` | git-ignored scan shows none tracked | High | In progress |
| R-037 | Use Gmail API or another documented method; Google API preferred | Email | Mandatory | Gmail API client libs; dry-run default + live-gated send (`RUN_GMAIL_LIVE=1`); minimal `gmail.send` scope; OAuth files outside repo (present — manual smoke OK); **readiness preflight** confirms files exist outside repo without reading contents | `gmail/sender.py`, `gmail/auth.py`, `gmail/send_report.py`, `gmail/preflight.py`, `tests/unit/gmail/` | Dry-run exit 0; mocked send maps message id; gmail preflight `status: ready` (files outside repo); **live send not run** | Med | In progress |
| R-038 | README is scientific/professional and includes Dec-POMDP framing | Docs | Strong | README adds Dec-POMDP section | `README.md` | Doc review | Low | Planned |
| R-039 | Formal Dec-POMDP tuple documented: ⟨n, S, {A_i}, P, R, {Ω_i}, O, γ⟩ | Docs | Strong | Tuple defined and mapped to engine | README / PRD section | Doc review against tuple | Low | Planned |
| R-040 | Emphasis on orchestration/pipeline over optimal strategy | Process | Strong | Full prompted MCP pipeline (observe→prompt→provider→parse→engine) with safe fallback; strategy is pluggable | `mcp_client/prompted_game_flow.py`, `llm/`, `tests/` | Prompted full game runs end-to-end | Low | In progress |
| R-041 | Q-learning / RL is optional creative, not required for baseline | Process | Optional | Deterministic baseline policies play full games with no RL; callable contract is pluggable | `agents/baseline.py`, `tests/unit/agents/`, `tests/unit/orchestration/` | Baseline runs full game without RL | Low | Done |
| R-042 | GUI is optional and must not risk core delivery | Process | Optional | No GUI on critical path; CLI/headless first | `PRD.md` non-scope | Core path runs headless | Low | Done |
| R-043 | Professional software guidelines are mandatory evaluation basis | Quality | Mandatory | Quality gates enforced each stage | `QUALITY.md` | Gate run each stage | Med | In progress |
| R-044 | README at repository root | Docs | Mandatory | `README.md` maintained at root | `README.md` | File exists, reviewed | Low | Done |
| R-045 | `docs/PRD.md` present | Docs | Mandatory | Top-level PRD maintained | `docs/PRD.md` | File exists, reviewed | Low | Done |
| R-046 | `docs/PLAN.md` present | Docs | Mandatory | Architecture plan maintained | `docs/PLAN.md` | File exists, reviewed | Low | Done |
| R-047 | `docs/TODO.md` present | Docs | Mandatory | Staged roadmap maintained | `docs/TODO.md` | File exists, reviewed | Low | Done |
| R-048 | Mechanism-specific PRDs present | Docs | Mandatory | One PRD per mechanism (engine, MCP, protocol, bonus, sender) | `docs/PRD_*.md` | Files exist, reviewed | Low | Done |
| R-049 | uv only — no pip/venv/requirements.txt | Quality | Mandatory | uv lockfile; ADR-0002 forbids alternatives | `uv.lock`, `pyproject.toml` | grep shows no pip/venv usage | Low | Done |
| R-050 | Ruff zero violations | Quality | Mandatory | Ruff config; fix every finding | `pyproject.toml` ruff config | `uv run ruff check .` clean | Low | Done |
| R-051 | Coverage ≥ 85% | Quality | Mandatory | `fail_under = 85` enforced | `pyproject.toml` | `uv run pytest --cov` ≥ 85 | Med | In progress |
| R-052 | Python files ≤ 150 code lines | Quality | Mandatory | Split modules to respect limit | Source tree | `wc -l` / size check per file | Low | In progress |
| R-053 | No secrets committed | Security | Mandatory | `.gitignore` + secret scan | `.gitignore`, scans | Secret-pattern grep clean | High | In progress |
| R-054 | `.env-example` present with placeholders only | Security | Mandatory | Placeholder env template at root | `.env-example` | File contains no real values | Low | Done |
| R-055 | Config drives parameters; not hardcoded | Quality | Mandatory | Central config loader/validator | `shared/config.py`, `config/*.json` | Loader tests + grep | Med | In progress |
| R-056 | SDK layer is the entrypoint | Quality | Strong | `sdk/sdk.py` façade is stable entry | `src/.../sdk/sdk.py` | Imports go through SDK | Low | Done |
| R-057 | API gatekeeper for external APIs | Quality | Strong | Single guarded module for Google/HTTP egress | Gatekeeper module, `SECURITY.md` | External calls only via gatekeeper | Med | Planned |
| R-058 | Test-driven development | Process | Strong | Tests precede/accompany each feature | Test suite, git history | Commits show tests-with-code | Med | In progress |
| R-059 | Meaningful Git history | Process | Strong | Staged, descriptive commits | git log | History review | Low | In progress |
| R-060 | Documented prompts (visible AI workflow) | Feedback | Mandatory | `PROMPTS.md` appended each stage | `docs/PROMPTS.md` | Prompt log present per stage | Low | In progress |
| R-061 | Cost/resource awareness | Feedback | Mandatory | Token/cost model per prompt/response (report fields); Gemini reports actual usage tokens when available; live smoke is cost-bounded + gated | `llm/cost.py`, `llm/gemini_provider.py`, `mcp_client/game_report.py`, `docs/COSTS.md` | Report shows tokens+cost; tests non-negative; live smoke gated | Med | In progress |
| R-062 | Quality gates defined and run | Quality | Mandatory | Gate list per stage + programmatic hardened gates (aggregate validation, token/overclaim scan status, run manifest) | `docs/QUALITY.md`, `run/hardened_smoke.py`, `run/validation.py` | Hardened smoke gates pass; manifest records gate status | Med | In progress |
| R-063 | Final gap audit performed | Process | Mandatory | Closing audit before submission | `docs/FINAL_GAP_AUDIT.md` | Audit completed, gaps closed | Med | Planned |
| R-064 | Extensibility addressed (Assignment 1 feedback) | Feedback | Strong | Pluggable strategy + config-driven design | `PLAN.md`, ADRs | Design review for seams | Med | In progress |
| R-065 | Evidence-backed claims (no overclaiming) | Feedback | Mandatory | Every claim cites a proof artifact; sanitized deterministic evidence pack committed | This matrix, `results/evidence/*.example.json`, `reporting/evidence.py` | Claim→artifact cross-check; evidence validates + token-free | Med | In progress |
| R-066 | Timezone fixed to Asia/Jerusalem for timestamps/reports | Report | Strong | `timezone` config used by reporter | `config/game.default.json` | Report timestamps in TZ | Low | Done |
| R-067 | Visibility radius is configurable (default 1) | Game | Strong | `visibility_radius` drives Chebyshev observation visibility | `config/game.default.json`, `observability/`, `tests/unit/observability/` | Tests: visible within / hidden outside radius | Low | Done |
| R-068 | Deterministic runs given a seed | Quality | Strong | Deterministic `run_id`/config fingerprint from group/stage/config-hash/seed; injectable timestamp/git | `run/identity.py`, `tests/unit/run/test_identity_and_manifest.py` | Same config+seed → same run_id; fingerprint changes on config change | Med | In progress |
| R-069 | Rate limiting / request budget enforced | Quality | Strong | Validated retry/timeout policy (`runtime.default.json`) + resource-guard model from `rate_limits.default.json` | `run/retry.py`, `run/rate_limit.py`, `config/runtime.default.json`, `tests/unit/run/` | Policy/guard validation + bounded retry tests | Med | In progress |
| R-070 | Auth tokens exchanged securely and revoked after bonus play | Security | Bonus-Mandatory | Out-of-band exchange; post-game revoke | `INTERGROUP_BONUS_PROTOCOL.md` | Revocation step logged | Med | Planned |

## Maintenance rules

1. New requirements get the next `R-0xx` ID; IDs are never reused.
2. A requirement may only be marked `Done` when its proof artifact exists and its
   validation method has actually been run (see ADR on evidence-first delivery).
3. The Risk Register (`RISK_REGISTER.md`) and Acceptance Criteria
   (`ACCEPTANCE_CRITERIA.md`) reference these IDs to keep traceability one-to-one.
