# CLOUD DEPLOYMENT GUIDE (future, gated)

> **Status: NOT deployed.** This is a step-by-step guide for a *later*, manual,
> gated deployment of the two MCP servers. No Cloud Run service has been created,
> no public URL exists, and nothing here runs automatically. All values are
> placeholders.

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

## Steps (run yourself; placeholders only)

1. **Preflight** (safe, local): `uv run python -m mars777_cop_thief.deployment.preflight`
   → must report `status: ok` before going further.
2. **Authenticate yourself** (not run here): `gcloud auth login`; select/create
   `<GOOGLE_CLOUD_PROJECT_ID>`; enable Cloud Run + Secret Manager + Artifact Registry.
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
