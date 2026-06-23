# PRD — MCP Servers

**Status:** Stage 0 draft (not yet implemented)

## Purpose

Expose the game engine to agents through **MCP over HTTP**, one server per role
(Cop, Thief). Servers are the only interface an agent uses to perceive and act.

## Transport & auth

- **HTTP transport from the start** (ADR-0003), enabling inter-group play.
- **Token auth:** every request must present a valid `MCP_AUTH_TOKEN`
  (bearer). Invalid/absent tokens are rejected with an auth error.
- Configurable URLs (`MCP_COP_SERVER_URL`, `MCP_THIEF_SERVER_URL`).

## Tools (planned)

- `look()` → role-scoped observation (radius-limited, never reveals full state).
- `move(direction)` → validated against engine; returns result/feedback.
- `status()` → match progress (move count, whether finished).

Tools map 1:1 onto engine interfaces; the server adds auth, validation, rate
limiting, and protocol framing only — no game logic lives here.

## Non-functional

- Stateless per request where possible; engine holds authoritative state.
- Rate limits from `config/rate_limits.default.json`.
- Structured logging with secret redaction; no tokens in logs.

## Acceptance

- A server starts, authenticates a token, serves `look`/`move`/`status`, and
  rejects unauthenticated calls. Integration tests use a local server and never
  require real credentials.
