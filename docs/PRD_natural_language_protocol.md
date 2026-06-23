# PRD — Natural-Language Protocol

**Status:** Stage 0 draft (not yet implemented)

## Purpose

Define how agents and MCP servers exchange perceptions and intents in
**natural language**, while remaining parseable, validated, and deterministic
enough to drive the engine.

## Direction: server → agent (perception)

A concise NL description of the role-scoped observation, e.g.:
> "You are the Cop at row 2, col 1. Within one cell you see: a barrier to the
> north; the grid edge to the west. The Thief is not visible. Move 4 of 25."

## Direction: agent → server (intent)

The agent replies with a single intended action expressed naturally, e.g.:
> "Move north-east."

The server maps this to a canonical action token (`NE`) via a constrained
parser. Ambiguous or illegal intents are rejected with NL feedback and the
agent is asked to restate.

## Canonicalization & validation

- Directions normalize to `{N,NE,E,SE,S,SW,W,NW}`; `stay` disabled by default.
- A strict mapping layer converts free text → canonical token; unknown text →
  clarification request (bounded retries via `retry_max_attempts`).
- All exchanges logged (redacted) for auditability and reproducibility.

## Acceptance

- Parser unit tests cover synonyms ("north east", "go NE", "up-right"),
  rejection of illegal/ambiguous intents, and retry behavior. No external calls.
