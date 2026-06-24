# CLOUD DEPLOYMENT GUIDE

> **Status: DEPLOYED (Stage 13C).** Both MCP services are live on Cloud Run in
> `api-mars-777` / `me-west1`. The actual results and reproduction commands are in
> the **Stage 13C — deployment results** section below; the steps that follow it
> remain the reusable, placeholder-based runbook for a fresh deploy. Auth tokens
> live only in git-ignored `.secrets/` and are never printed or committed.

## Stage 13C — deployment results (live)

| Role | Service | Public URL | Revision |
|------|---------|------------|----------|
| Cop | `mars777-cop-mcp` | `https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app` | `mars777-cop-mcp-00001-jqk` |
| Thief | `mars777-thief-mcp` | `https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app` | `mars777-thief-mcp-00001-5nk` |

- **Project/region:** `api-mars-777` / `me-west1`. **Build:** `gcloud run deploy
  --source .` (Cloud Build from the repo `Dockerfile`).
- **APIs enabled this stage (only those strictly required):** `run.googleapis.com`,
  `cloudbuild.googleapis.com`, `artifactregistry.googleapis.com`.
- **IAM:** `--allow-unauthenticated` (public at the IAM layer) **because the MCP app
  enforces token auth** on protected tools; a raw unauthenticated `GET /` returns
  `404` and `GET /mcp` returns `406` (app-handled, **not** an IAM `403`).
- **Env per service:** `MCP_ROLE=cop|thief` plus the role token
  (`COP_MCP_TOKEN`/`THIEF_MCP_TOKEN`), supplied via a git-ignored
  `--env-vars-file .secrets/<role>.env.yaml`. `PORT` is injected by Cloud Run.
- **Tokens:** generated locally with Python `secrets` (32-byte URL-safe), stored
  only under `.secrets/` (git-ignored + docker-ignored), never printed/committed.

**Public smoke (token-safe; reproduce):**

```bash
set -a; . .secrets/cloud-run.local.env; set +a   # load tokens without echoing
COP_MCP_URL=https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app \
THIEF_MCP_URL=https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app \
uv run python scripts/public_cloud_smoke.py
```

Result: `passed: true` — Cop & Thief both reject a bad token (`unauthorized`) and
accept the correct token (`health_ok`, role-correct, hidden opponent not leaked,
thief has no barrier tool). Sanitized evidence (no tokens):
`results/evidence/cloud_deployment.example.json`. **No live Gmail send and no
inter-group bonus run were performed.**

**Full public-cloud game + official report dry-run (Stage 14A):**

```bash
set -a; . .secrets/cloud-run.local.env; set +a   # tokens, never echoed
uv run python scripts/public_cloud_final_dry_run.py
```

Plays the full **6 sub-games** over the public `/mcp` URLs, builds and
**schema-validates** the official internal report (real public URLs + repo,
`cloud_status: deployed`), and runs the Gmail sender in **dry-run only**. Result:
6/6 decided (totals cop 30 / thief 60), `report_schema_valid: true`, bad token
rejected, `gmail_dry_run_status: dry_run` / `body_json_valid: true`,
`live_gmail_sent: false`. Evidence (token-free):
`results/evidence/public_cloud_full_game.example.json` (full report) and
`results/evidence/final_report_dry_run.example.json` (summary).

> The runbook below is the reusable, **placeholder-based** procedure for a clean
> deploy; `config/cloud.default.json` stays the not-yet-deployed packaging
> template (so the packaging preflight remains a valid pre-deploy gate), while the
> live state is recorded in the evidence file above.

# CLOUD DEPLOYMENT RUNBOOK (reusable, placeholders)

> The two MCP servers deploy from one role-aware image. Values below are
> placeholders for a fresh deploy.

## Target

**Primary:** Google Cloud Run — containerized HTTP services fit the two remote
MCP servers well. **Alternatives:** any HTTPS container platform (Fly.io, Render,
a container on a VM) also works; Cloud Run is the documented default, not the only
option.

## Architecture

Two independent services from **one role-aware image** (`Dockerfile`):

| Service (placeholder) | Role | Token env var |
|-----------------------|------|---------------|
| `mars777-cop-mcp`     | `MCP_ROLE=cop`   | `COP_MCP_TOKEN`   |
| `mars777-thief-mcp`   | `MCP_ROLE=thief` | `THIEF_MCP_TOKEN` |

The container entrypoint (`mcp_servers/cloud_entrypoint.py`) reads `MCP_ROLE`,
binds `0.0.0.0`, reads `PORT` (injected by the platform), and **fails fast** if
the role's token env var is missing. The token value is never logged. The LLM
stays outside the servers; tools remain role-safe (no hidden-state leakage).

## Stage 13B — live-readiness preflight (run this first)

Before any deploy, run the **combined live-readiness preflight**. It is read-only:
it makes no cloud calls that change state and sends no Gmail.

```bash
uv run python -m mars777_cop_thief.deployment.live_readiness
```

It reports three groups and the remaining manual blockers:

- **Gmail OAuth files** — checks that `GOOGLE_OAUTH_CLIENT_SECRETS` /
  `GOOGLE_OAUTH_TOKEN_PATH` point at existing files **outside** the repo. It only
  stats paths; it never reads contents. `live_send_enabled` is `false` unless
  `RUN_GMAIL_LIVE=1`. Your real paths stay outside Git (use placeholders in docs).
- **Cloud / gcloud (read-only)** — whether `gcloud` is installed, whether an
  account is active, the active project vs the expected **`api-mars-777`**, the
  intended **region** (`CLOUD_RUN_REGION`, recommended `me-west1`), and a
  best-effort billing read. **Billing disabled** is a blocker; **billing unknown**
  is a warning. Missing gcloud / no auth are blockers, never crashes. It runs no
  `deploy`/`build`/`create`/`enable` command.
- **Packaging** — folds in the Stage 13A packaging preflight status.

The command exits `0` once the checks complete even if blockers remain; resolve
every listed blocker before continuing. Typical first-time blockers: install
gcloud, `gcloud auth login`, select `api-mars-777`, **enable billing**, confirm
the `me-west1` region. No public MCP URLs exist yet at this point.

## Steps (run yourself; placeholders only)

1. **Preflight** (safe, local): `uv run python -m mars777_cop_thief.deployment.preflight`
   then `uv run python -m mars777_cop_thief.deployment.live_readiness`
   → packaging must report `status: ok` and the live-readiness blockers list must
   be empty before going further.
2. **Authenticate yourself** (not run here): `gcloud auth login`; select
   `<GOOGLE_CLOUD_PROJECT_ID>` (this project: `api-mars-777`); **enable billing**;
   enable Cloud Run + Secret Manager + Artifact Registry. Choose region
   `<REGION>` (recommended `me-west1`).
3. **Create secrets** (never commit tokens): store strong random values as
   `<SECRET_NAME>` for `COP_MCP_TOKEN` and `THIEF_MCP_TOKEN` in Secret Manager.
4. **Build & push the image**: `gcloud builds submit --tag <IMAGE>` (one image,
   role chosen at deploy time).
5. **Deploy two services** (`scripts/cloud_run_deploy_template.sh`, gated by
   `RUN_CLOUD_DEPLOY=1`): set `MCP_ROLE=cop`/`thief` and inject the token via
   `--set-secrets`; choose `<REGION>`.
6. **Record public URLs**: set `COP_MCP_PUBLIC_URL` / `THIEF_MCP_PUBLIC_URL` in
   your local `.env` only (never commit). Update `config/cloud.default.json`
   `cloud_status` away from `not_deployed` **only after** real URLs respond.
7. **Verify**: from a client, call `health_check` and an authenticated
   `get_observation` over HTTPS; confirm a wrong token is rejected and the thief
   service exposes no barrier tool. Re-run the local `game_smoke` / `hardened_smoke`
   for a regression baseline.

## Rollback / token revoke checklist

- **Rollback**: `gcloud run services update-traffic <SERVICE> --to-revisions <PREV>=100`,
  or delete the new revision/service.
- **Revoke a token**: rotate the value in Secret Manager and redeploy the affected
  service (`:latest`); revoke any token shared for inter-group play after the match.
- **Audit**: confirm no token/secret appears in build logs, service env, or
  results; re-run `uv run python -m mars777_cop_thief.deployment.preflight`.

## Security notes

- Tokens come from the platform secret manager / runtime env only — never image
  build args, `Dockerfile ENV`, logs, docs examples, or committed files.
- `.dockerignore` excludes `.env`, `credentials.json`, `token.json`, `.venv`,
  caches, tests, results, and course documents from the build context.
- Endpoints stay token-protected; the minimal surface is the role-safe MCP tools.
