"""Deterministic baseline policies for local self-play.

The cop steps toward the thief; the thief steps away from the cop. Both are pure
functions of state with a fixed direction ordering, so play is reproducible with
no randomness and no external service. A policy returns ``None`` only when the
actor has no legal move at all.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import DIRECTION_DELTAS, Action, PlayerRole, Position
from mars777_cop_thief.game.rules import move_violation, step_target
from mars777_cop_thief.game.state import SubGameState

# Fixed tie-break / fallback ordering (engine's canonical compass order).
CANONICAL_DIRECTIONS: tuple[str, ...] = tuple(DIRECTION_DELTAS)


def chebyshev(a: Position, b: Position) -> int:
    """King-move distance, matching 8-direction one-step movement."""
    return max(abs(a.row - b.row), abs(a.col - b.col))


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


def legal_moves(state: SubGameState, role: PlayerRole) -> list[tuple[str, Position]]:
    """Legal one-step moves for ``role`` in canonical direction order."""
    origin = state.position_of(role)
    moves: list[tuple[str, Position]] = []
    for direction in CANONICAL_DIRECTIONS:
        target = step_target(origin, direction)
        if move_violation(origin, target, state.rows, state.cols, state.barriers, False) is None:
            moves.append((direction, target))
    return moves


def first_legal_action(state: SubGameState, role: PlayerRole) -> Action | None:
    """First legal move (canonical order), or None if the actor is stuck."""
    moves = legal_moves(state, role)
    if not moves:
        return None
    direction, target = moves[0]
    return Action.move(role, target, direction)


def _step_policy(state: SubGameState, role: PlayerRole, *, toward: bool) -> Action | None:
    moves = legal_moves(state, role)
    if not moves:
        return None
    other = state.position_of(_opponent(role))
    current = chebyshev(state.position_of(role), other)
    if toward:
        preferred = [m for m in moves if chebyshev(m[1], other) < current]
        chosen = min(preferred, key=lambda m: chebyshev(m[1], other)) if preferred else moves[0]
    else:
        preferred = [m for m in moves if chebyshev(m[1], other) > current]
        chosen = max(preferred, key=lambda m: chebyshev(m[1], other)) if preferred else moves[0]
    return Action.move(role, chosen[1], chosen[0])


def cop_policy(state: SubGameState) -> Action | None:
    """Cop baseline: step toward the thief, else first legal fallback."""
    return _step_policy(state, PlayerRole.COP, toward=True)


def thief_policy(state: SubGameState) -> Action | None:
    """Thief baseline: step away from the cop, else first legal fallback."""
    return _step_policy(state, PlayerRole.THIEF, toward=False)
