# SUBMISSION CHECKLIST

Strict checklist for the final review. Boxes are checked only when verified.

> **Stage 15G closeout:** the in-repo deliverables are **complete**. The official
> self-play report is built/validated (dry-run + draft), and the mutually-agreed
> inter-group `bonus_game` report was **sent live to Dr. Segal** and the **partner
> (orcai-mj) confirmed they sent their matching report**; `result_hash a0fdf72d…`
> matched, `mutual_agreement: true`. Remaining items are **external** (Moodle form) and
> **post-grading** (token revocation, optional Cloud Run teardown). 401 tests, 100%
> coverage; no tokens or student national IDs committed.

## Repository & packaging
- [x] `uv sync` succeeds from a clean checkout (locked deps; all `uv run` gates pass)
- [x] Professional `src/` package layout
- [x] Every Python source/test/script file < 150 logical lines (max 149)
- [x] `pyproject.toml` configures pytest, coverage, ruff

## Quality gates
- [x] `uv run pytest` passes (401 tests)
- [x] Coverage 100% (`fail_under = 85`)
- [x] `uv run ruff check .` clean
- [x] `uv run ruff format --check .` clean
- [x] `git status --short --ignored` shows no stray artifacts (only ignored caches/`.secrets`)

## Security
- [x] No secrets committed (`.env`, credentials, tokens, keys)
- [x] `.gitignore` covers all secret/artifact patterns
- [x] `.env-example` contains placeholders only
- [x] MCP token auth enabled; OAuth files external; revoke story documented

## Functionality
- [x] Game engine matches assignment rules (grid, movement, capture, scoring)
- [x] MCP servers run over HTTP and expose perception/action tools
- [x] Natural-language protocol implemented and validated
- [x] Cop & Thief agents play through MCP
- [x] Orchestrator runs `num_sub_games` and aggregates results
- [x] Google report sender emails final results (bonus_game sent live to the lecturer)
- [x] Bonus inter-group play demonstrated (official 6-sub-game match, mutually agreed)

## Reports & evidence
- [x] Official internal report schema defined and **validated** (`reporting/`)
- [x] Report is JSON-only / email-body ready and **token-safe** (no token keys/values)
- [x] Bonus/inter-group schema example exists (no real run claimed; `bonus_claim=false`)
- [x] Sanitized, deterministic evidence pack committed under
      `results/evidence/*.example.json` (no tokens, no full event logs)
- [x] Optional real provider (Gemini) adapter implemented behind the LLM interface
      (opt-in; no key required for tests)
- [ ] Optional real-Gemini live smoke run locally with `RUN_GEMINI_LIVE=1` + key
      (evidence of real integration; not run in default validation)
- [x] Gmail JSON report sender implemented; dry-run validates + builds JSON-only
      body without sending (`uv run python -m mars777_cop_thief.gmail.send_report`)
- [x] Email body proven JSON-only (decodes/parses back to the report object)
- [x] Hardened run smoke passes with a secret-free manifest + aggregate validation
      (`uv run python -m mars777_cop_thief.run.hardened_smoke` → `status: ok`)
- [x] Deterministic `run_id`/config fingerprint; failures classified; bounded retries
- [x] Cloud deployment packaging + preflight ready (Dockerfile, role entrypoint,
      `deployment.preflight` → `status: ok`); no secrets in image
- [x] Live-readiness preflight ready (`deployment.live_readiness` exits 0, lists
      blockers; read-only — no live send, no deploy)
- [x] Gmail OAuth files present **outside the repo** (manual smoke: draft + calendar
      event OK); `gmail.preflight` → `status: ready` without reading file contents
- [x] Cloud live blockers cleared: `gcloud` installed + authenticated, project
      `api-mars-777` active, **billing enabled**, region `me-west1` confirmed
- [x] Two MCP services **deployed** at public, app-token-authenticated Cloud Run
      URLs (`mars777-cop-mcp`, `mars777-thief-mcp` in `api-mars-777`/`me-west1`)
- [x] Public HTTPS smoke passed: both reject a bad token, accept the correct token
      (`scripts/public_cloud_smoke.py` → `passed: true`)
- [x] Sanitized deployment evidence committed, no token values
      (`results/evidence/cloud_deployment.example.json`)
- [x] Cop & Thief public URLs recorded in README + evidence; tokens only in
      git-ignored `.secrets/` (never committed/printed)
- [x] Real `cop_mcp_url`/`thief_mcp_url` recorded in tracked evidence + README
      (deployed-state in `results/evidence/cloud_deployment.example.json`;
      `config/cloud.default.json` deliberately stays the not-deployed packaging
      template so the packaging preflight remains a valid pre-deploy gate)
- [x] Full **6-sub-game game over the public `/mcp` URLs** + official report built
      and **schema-validated** (`scripts/public_cloud_final_dry_run.py`;
      `results/evidence/public_cloud_full_game.example.json`)
- [x] Final official report **Gmail dry-run** passed with that report (`dry_run`,
      `body_json_valid: true`); **no live email sent**
      (`results/evidence/final_report_dry_run.example.json`)
- [x] Official report supports the **two real students** (MaRs-777) at runtime; real
      identities load from a local **git-ignored** file (`.secrets/students.local.json`)
- [x] Tracked evidence **redacts** student national IDs (`id: REDACTED` + privacy
      flags); no national-ID value in any tracked file
      (`results/evidence/public_cloud_full_game.example.json`)
- [x] **Git history scrubbed** of student national IDs (`git filter-repo` +
      `--force-with-lease`); all reachable history ID-free, verified in a fresh
      clone (0 matches); repo stayed public (GitHub internal-cache caveat noted)
- [x] Gmail **draft preview** of the official JSON report created (to the student's
      own account, **not** the lecturer); subject `PREVIEW ONLY - …`; JSON-only body,
      schema-valid, no placeholders; **not sent** (`scripts/gmail_draft_preview.py`,
      `results/evidence/gmail_draft_preview.example.json`) — this is a preview, **not**
      the official submission
- [ ] Real internal report emailed **to the lecturer** via `RUN_GMAIL_LIVE=1` with
      external OAuth files (optional live send; not run yet)
- [x] Inter-group bonus **readiness gate** prepared (`bonus_partner_readiness.py`):
      self cloud ready, local partner intake + strategy, sanitized evidence
      (no tokens/IDs) — **prepared, not the game**
- [x] **Live partner compatibility smoke passed** (Stage 15C,
      `bonus_partner_live_smoke.py`): partner endpoints reachable; unauthorized
      rejected; authorized accepted; setup/observe/my_move/state OK; role identity
      consistent per server; 0-based `[row,col]`; thief-first; **5x5 and 8x8** warm-ups
      pass. Adapter reconciled to the partner's confirmed contract; sanitized evidence
      (`results/evidence/bonus_partner_live_smoke.example.json`,
      `partner_smoke_passed: true`, no tokens/IDs) — **compatibility only, not the game**
- [x] Official rules frozen by mutual written agreement (Stage 15D): **8x8**, 6 sub-games,
      ≤25 moves, ≤5 cop-only barriers, diagonal, thief-first, 0-based `[row, col]`
- [x] **Official inter-group bonus game played** (Stage 15D, `scripts/run_bonus_game.py`):
      automated referee, **no human moves**; both directions (Set A MaRs-777 Cop vs
      orcai-mj Thief ×3, Set B orcai-mj Cop vs MaRs-777 Thief ×3); **6/6 decided on 8x8**;
      totals_by_group **MaRs-777 30 / orcai-mj 90**; canonical `bonus_game` JSON +
      token-free handoff with `result_hash`; sanitized evidence (`bonus_game_*`, IDs
      redacted, no tokens); `validation_status: valid`
- [x] **Partner confirmation received & mutual agreement finalized** (Stage 15E): orcai-mj
      confirmed the canonical result and rules in writing; `mutual_agreement: true`,
      `partner_confirmation_status: confirmed`, `bonus_claim: true` — result fields
      untouched, `result_hash` unchanged (`a0fdf72d…`). Final artifacts:
      `bonus_game_report_final_agreed`, `bonus_game_partner_handoff_final` (with a derived
      `hash_method` the partner can reproduce), `bonus_game_mutual_agreement`
- [x] **Bonus_game Gmail draft/preview prepared only** (Stage 15E,
      `scripts/bonus_finalize_agreement.py`): JSON-only bonus_game draft to the lecturer
      created in Gmail (`gmail_draft_created: true`) and **not sent** — `RUN_GMAIL_LIVE`
      unset, `live_gmail_sent: false`, `bonus_email_sent: false`; body is ID-redacted
- [x] **Final `bonus_game` report sent live to the lecturer** (Stage 15F,
      `scripts/bonus_send_final_email.py`): one Gmail message to `rmisegal+uoh26b@gmail.com`,
      JSON-only body with the top-level `result_hash` (`a0fdf72d…`), `mutual_agreement: true`,
      `partner_confirmation_status: confirmed`; partner independently reproduced & matched the
      hash and is sending their matching report. `live_gmail_sent: true`,
      `bonus_email_sent: true`, **`internal_game_sent: false`**; idempotency guard prevents a
      second send. Sanitized evidence `results/evidence/bonus_game_email_sent.example.json`
      (no tokens/OAuth/IDs)
- [x] **Partner (orcai-mj) confirmed they sent their matching `bonus_game` report** to
      Dr. Segal (Stage 15G); recorded in `results/evidence/final_submission_closeout.example.json`
      (`partner_email_confirmed_sent: true`) — no screenshots/raw headers/ids stored
- [ ] `internal_game` report sent live to the lecturer — **not sent by design**; the
      submitted email is the mutually-agreed `bonus_game` report (internal report remains
      built/validated with a dry-run + student-only draft)
- [ ] Match-scoped tokens revoked after the match and recorded — **post-grading** (deferred)

## Documentation & measurement
- [x] PRDs, PLAN, DECISIONS, PROMPTS complete and current (PROMPTS logged per stage)
- [ ] COSTS includes measured real-LLM figures — N/A: agents are deterministic
      (`fake_local`/observed policies), so no real LLM spend; live Gemini stays opt-in
- [x] QUALITY gates documented and reproducible
- [x] `FINAL_GAP_AUDIT.md` completed and closed (Stage 15G)

## Process
- [x] No `git add .` used; staging was explicit
- [x] Commits made only after review

## Remaining for Moodle / submission form (external to the repo)
- [ ] Submit the assignment via the Moodle form/PDF (repo URL + summary) — done by a human
- [ ] (Post-grading) revoke match-scoped tokens; optionally tear down Cloud Run
