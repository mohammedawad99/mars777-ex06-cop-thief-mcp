# SECURITY

## Principles

- **No secrets in the repository.** API keys, tokens, and OAuth files are never
  committed. They are provided locally via `.env` (ignored) and documented as
  placeholders in `.env-example`.
- **Least exposure.** MCP servers bind to explicit URLs and require token auth.

## MCP authentication

- All MCP communication uses **HTTP with a token check** from the start.
  Requests without a valid token are rejected.
- Tokens are random, per-environment, and rotated if exposed. They live only in
  `.env`, never in code, config defaults, or logs (see `redact_keys` in
  `config/logging.default.json`).

### Local MCP token handling (Stage 5)

- Each role server reads its expected token from an environment variable named in
  `config/mcp.local.default.json` — `COP_MCP_TOKEN` for the Cop server and
  `THIEF_MCP_TOKEN` for the Thief server. Placeholders (not real tokens) are in
  `.env-example`; real values live only in the untracked `.env`.
- Stage 5 uses an explicit **`auth_token` tool argument** as **local development
  auth** (see ADR-0021), checked by `mcp_servers/auth.py`. A mismatch returns a
  **structured unauthorized result** (never raises) and the **real token is never
  logged or returned** — the result's `auth_token` field is `***redacted***`.
- This is to be **upgraded to request-metadata / OIDC** auth before any cloud or
  inter-group exposure. No public URLs are deployed in this stage.

### Dummy local tokens vs. real secrets (Stage 6 smoke)

- The E2E smoke (`mcp_client/smoke.py`) uses **dummy local tokens** generated in
  process memory (e.g. `dummy-local-cop-token`) and injects them into the server
  **subprocess environment** only. These are **not secrets** — they never grant
  access to anything beyond a throwaway local server bound to `127.0.0.1` on a
  free port for the duration of the smoke, and they are **never written to disk**
  or committed.
- Real tokens (for any future non-local use) still come only from the untracked
  `.env`; `.env-example` holds placeholders. The secret scan's only `.env-example`
  matches are those documented placeholders, not real values.

### MCP token rotation / revocation

1. Generate a fresh random value for `COP_MCP_TOKEN` / `THIEF_MCP_TOKEN` in `.env`.
2. Restart the affected local server so it reloads the new expected token.
3. For inter-group play later, exchange match-scoped tokens out-of-band and revoke
   them after the session (see `INTERGROUP_BONUS_PROTOCOL.md`).

## Google OAuth credential handling

- The report sender uses Google/Gmail OAuth. The client secrets
  (`credentials.json`) and the issued token (`token.json`) are **kept outside
  Git** and referenced via `GOOGLE_OAUTH_CLIENT_SECRETS` / `GOOGLE_OAUTH_TOKEN_PATH`.
- `.gitignore` blocks `credentials.json`, `token.json`, `client_secret*.json`,
  `*_oauth*.json`, `service_account*.json`, and key files.

## Revoke story

If a credential is ever exposed:
1. Revoke the affected key/token at its provider:
   - Google: revoke the token in the Google Account → Security → Third-party
     access, and reset the OAuth client secret in Google Cloud Console.
   - LLM provider: rotate the API key in the provider dashboard.
   - MCP: generate a new `MCP_AUTH_TOKEN` and redeploy.
2. Delete the local artifact and remove any leaked copy from history if it was
   ever committed (it must not be).
3. Issue fresh credentials, update `.env`, and re-test.

## Secret hygiene checklist

- `git status --short --ignored` shows no tracked secrets/artifacts.
- `.env` exists only locally; only `.env-example` is committed.
- Logs redact sensitive keys; no secret is printed to stdout.
