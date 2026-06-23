# PRD — Game Engine

**Status:** Stage 0 draft (not yet implemented)

## Purpose

The authoritative, deterministic core that holds game state and enforces all
rules. Agents and MCP servers never mutate state directly — they request
actions the engine validates and applies.

## Entities

- **Board:** `grid_size` (default 5×5); cells indexed `(row, col)`.
- **Barriers:** up to `max_barriers` impassable cells.
- **Players:** Cop and Thief, each at a cell.
- **Match state:** move count, turn, status (running/cop_win/thief_win), seed.

## Rules

- Movement: 8 directions (`N, NE, E, SE, S, SW, W, NW`); `stay` disabled unless
  documented/negotiated (`allow_stay = false`).
- A move is rejected (or treated as no-op per spec) if it leaves the grid or
  enters a barrier.
- Capture: Cop captures when both occupy the same cell → `cop_win`.
- Timeout: if Thief survives `max_moves` → `thief_win`.
- Visibility: each player perceives cells within `visibility_radius` (= 1).
- Scoring: `cop_win=20`, `thief_win=10`, `cop_loss=5`, `thief_loss=5`.

## Determinism

- All randomness (start positions, barrier layout) derives from a seed so a run
  is reproducible. Sanity grid sizes 2×2…5×5 must all be supported.

## Interfaces (planned)

- `reset(seed) -> State`
- `legal_moves(role) -> list`
- `step(role, move) -> State`
- `observe(role) -> Observation` (radius-limited)
- `result() -> Outcome | None`

## Acceptance

- Unit tests cover movement legality, barrier/edge blocking, capture, timeout,
  scoring, and determinism across all sanity grid sizes. No external calls.
