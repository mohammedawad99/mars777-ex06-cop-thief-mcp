# INTER-GROUP BONUS PROTOCOL

**Group:** MaRs-777 (`mars777`) · **Stage:** 1 · **Status:** Operational procedure

> **Scope note — read first.** This document defines **operational coordination
> between two teams**, not a hardcoded message format between agents. The agents
> still communicate in **free natural language** (see
> `PRD_natural_language_protocol.md`). Nothing here introduces a rigid numeric
> wire protocol. What is standardised is how two human teams *set up, run, log,
> and reconcile* a cross-group match — the pipeline around the game, not the
> language inside it.

## 0. Roles and prerequisites

- Each team runs its own **Cop MCP server** and **Thief MCP server** over HTTP
  with token auth (ADR-0003, R-004, R-010).
- Each team has the baseline engine rules implemented and config-driven
  (default 5×5, 6 sub-games, ≤ 25 moves, ≤ 5 Cop barriers, 8-direction movement,
  no stay) — see `config/game.default.json`.
- Each team can produce a JSON report (R-031, R-033) and a bonus report
  (R-034).

## 1. Exchange Cop/Thief URLs

Each team shares **two public URLs**: its Cop MCP URL and its Thief MCP URL
(R-009). URLs are exchanged over a normal team channel (email/chat). Reachability
is confirmed by a simple authenticated health/look call from the other side
*before* the match window. If a URL is behind NAT/firewall, the team uses a
hosted or tunneled public endpoint (RK-08).

## 2. Exchange auth tokens securely

Tokens are exchanged **out-of-band** (not committed, not in agent messages, not
in shared logs). Use a direct private channel. Each team issues a **match-scoped
token** to the other team that is easy to revoke afterward (R-070). Tokens are
never embedded in reports; reports reference URLs only.

## 3. Agree board size and origin

Both teams confirm:

- **Board size** — default 5×5; smaller sanity sizes (2×2…4×4) may be used for a
  warm-up interop check first (R-014).
- **Coordinate origin and axes** — which corner is `(0,0)`, and the direction of
  increasing row/column, so "NE" means the same thing on both sides. This is a
  one-line natural-language agreement, recorded in the match notes; it is **not**
  a protocol field exchanged by agents.

## 4. Agree turn order

Teams agree who moves first and the turn alternation (turn-based, R-011). The
default is Cop-first; any deviation is written into the match notes.

## 5. Agree whether any additional rules are used

Teams state explicitly whether any **extra rules** apply (e.g. allowing `stay`,
adjusted visibility radius, different barrier budget). Per baseline, `stay` is
disabled unless **both teams** explicitly negotiate and document it (R-020). Any
extra rule must be config-expressible on both sides — no code forks.

## 6. Confirm baseline rules if no extras

If no extras are agreed, both teams confirm the **baseline ruleset** in writing:
5×5, 6 sub-games, ≤ 25 moves each, 8-direction movement, no stay, Cop barriers
≤ 5, Thief no barriers, capture on shared cell, Thief wins on survival, scoring
Cop-win 20/5 and Thief-win 10/5 (R-016–R-030). This written confirmation is the
reference if a dispute arises.

## 7. Run 3 sub-games one way, then 3 with roles swapped

A full cross-group game is **6 sub-games** (R-015), split for fairness:

1. **Set A (3 sub-games):** our Cop vs. their Thief (or as agreed).
2. **Set B (3 sub-games):** roles swapped — our Thief vs. their Cop.

Each sub-game is capped at 25 moves (R-016). Both teams run against the agreed
URLs with the exchanged tokens.

## 8. Keep logs

Both teams keep full structured transcripts for **every** sub-game: raw NL
messages, the `interpreted_action` for each, the resulting engine state, and any
illegal-move rejections (R-025, R-026). Logs are the authoritative dispute
record (RK-10, RK-17).

## 9. Compare reports

After all 6 sub-games, each team independently computes its JSON report. Teams
**compare**:

- Per-sub-game outcomes and move counts.
- `totals_by_group` (R-034).
- Any flagged illegal moves or interpretation disagreements.

## 10. Send matching JSON reports

When results agree, both teams set `mutual_agreement: true` and produce
**matching bonus reports** containing both group names, both GitHub repos, the
four MCP URLs, students, `sub_games`, `totals_by_group`, `bonus_claim`, and
`mutual_agreement` (R-034). The instructor email body is JSON only (R-032).

## 11. Dispute handling

If the two reports disagree:

1. Both teams replay the contested sub-game(s) from their transcripts.
2. The authoritative engine state + logged `interpreted_action` decide legality
   (R-010 boundary, R-025/R-026 logs).
3. If reconciliation fails, `mutual_agreement` is set to `false` and
   `bonus_claim` is **not** asserted as accepted — the bonus may be rejected
   (R-035, RK-09). The disagreement and both transcripts are retained as evidence.

## 12. Revoke tokens after the game

Once reports are exchanged, **both teams revoke** the match-scoped tokens issued
in step 2 and record the revocation (R-070, RK-24). Public URLs may be taken down
or rotated afterward.

---

### Why this is operational, not a wire protocol

Steps 1–12 coordinate **teams and infrastructure**: URLs, tokens, agreed config,
fairness, logging, and reconciliation. The **agents themselves** still speak free
natural language and the **engine** remains the authority on legal moves. This
separation is recorded as an architecture decision in `DECISIONS.md`
(operational inter-group protocol separated from agent language).
