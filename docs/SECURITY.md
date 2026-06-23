# SECURITY

## Principles

- **No secrets in the repository.** API keys, tokens, and OAuth files are never
  committed. They are provided locally via `.env` (ignored) and documented as
  placeholders in `.env-example`.
- **Least exposure.** MCP servers bind to explicit URLs and require token auth.

## MCP authentication

- All MCP communication uses **HTTP with a bearer/token check** from the start
  (`MCP_AUTH_TOKEN`). Requests without a valid token are rejected.
- Tokens are random, per-environment, and rotated if exposed. They live only in
  `.env`, never in code, config defaults, or logs (see `redact_keys` in
  `config/logging.default.json`).

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
