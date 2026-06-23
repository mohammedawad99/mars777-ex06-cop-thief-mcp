"""Pure rule predicates for movement and barrier placement.

Each helper returns a ``RuleViolation`` describing why an action is illegal, or
``None`` when it is legal. No state is mutated here.
"""

from __future__ import annotations

from collections.abc import Iterable

from mars777_cop_thief.game.models import DIRECTION_DELTAS, Position, RuleViolation


def in_bounds(pos: Position, rows: int, cols: int) -> bool:
    """Return True if ``pos`` lies on a ``rows`` x ``cols`` board."""
    return 0 <= pos.row < rows and 0 <= pos.col < cols


def step_target(origin: Position, direction: str) -> Position | None:
    """Resolve a one-step ``direction`` from ``origin``; None if unknown."""
    delta = DIRECTION_DELTAS.get(direction)
    if delta is None:
        return None
    return Position(origin.row + delta[0], origin.col + delta[1])


def move_violation(
    origin: Position,
    target: Position,
    rows: int,
    cols: int,
    barriers: Iterable[Position],
    allow_stay: bool,
) -> RuleViolation | None:
    """Validate a move from ``origin`` to ``target`` against the baseline rules."""
    drow, dcol = target.row - origin.row, target.col - origin.col
    if drow == 0 and dcol == 0:
        return None if allow_stay else RuleViolation.STAY_NOT_ALLOWED
    if max(abs(drow), abs(dcol)) != 1:
        return RuleViolation.NOT_ONE_STEP
    if not in_bounds(target, rows, cols):
        return RuleViolation.OUT_OF_BOUNDS
    if target in set(barriers):
        return RuleViolation.INTO_BARRIER
    return None


def barrier_violation(
    target: Position,
    rows: int,
    cols: int,
    barriers: Iterable[Position],
    occupied: Iterable[Position],
) -> RuleViolation | None:
    """Validate placing a barrier on ``target`` (placement/limit checks elsewhere)."""
    if not in_bounds(target, rows, cols):
        return RuleViolation.BARRIER_OUT_OF_BOUNDS
    if target in set(occupied):
        return RuleViolation.BARRIER_ON_OCCUPIED
    if target in set(barriers):
        return RuleViolation.BARRIER_EXISTS
    return None
