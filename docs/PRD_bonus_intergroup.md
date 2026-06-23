# PRD — Bonus: Inter-Group Play

**Status:** In-scope and **mandatory for architecture** (ADR-0005)

## Stance

Although inter-group play is officially a bonus, this project treats it as
**mandatory scope for architecture and planning**. The system is designed from
the start so that another group's agent or server can participate without
re-architecting. Implementation lands **after a stable in-group baseline**.

## What "inter-group" means here

Two groups' systems interoperate across a network boundary:
- Our agent plays against another group's MCP server (or vice versa), and/or
- Our Cop server hosts a match where the opposing role is driven by another
  group's agent.

## Architectural implications (already reflected)

- **HTTP MCP transport from day one** (ADR-0003) — no stdio-only assumptions.
- **Token auth** so external participants authenticate explicitly.
- **Shared natural-language protocol** (`PRD_natural_language_protocol.md`) so
  message formats are interoperable, not internal-only.
- **Config-driven server URLs** so endpoints can point at another group.

## Interoperability requirements

- Agreed protocol version (`version` field) and direction vocabulary.
- Compatible scoring and `max_moves` / `num_sub_games`, or an agreed match
  config exchanged before play.
- Clear error/auth semantics so a foreign client fails safely.

## Acceptance

- A documented, repeatable inter-group match runs end-to-end over HTTP with
  token auth and produces an aggregated, reportable result.
