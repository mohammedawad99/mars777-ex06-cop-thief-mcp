"""Observation-based deterministic policies (no access to hidden full state).

Decisions use only the agent's Observation. When the opponent is visible the cop
steps toward it and the thief steps away; when it is hidden, each role uses a
deterministic board-relative fallback — the cop patrols toward the board centre,
the thief explores toward the edges. With ``visibility_radius >= 1`` every
one-step target is itself visible, so a chosen move never enters an unseen
barrier.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import DIRECTION_DELTAS, Action, PlayerRole, Position
from mars777_cop_thief.game.rules import in_bounds, step_target
from mars777_cop_thief.observability.observation import Observation
from mars777_cop_thief.observability.visibility import chebyshev

CANONICAL_DIRECTIONS: tuple[str, ...] = tuple(DIRECTION_DELTAS)


def board_center(obs: Observation) -> Position:
    """Deterministic centre cell of the observed board."""
    return Position((obs.rows - 1) // 2, (obs.cols - 1) // 2)


def observed_legal_moves(obs: Observation) -> list[tuple[str, Position]]:
    """One-step moves that are in bounds and clear of visible barriers."""
    moves: list[tuple[str, Position]] = []
    for direction in CANONICAL_DIRECTIONS:
        target = step_target(obs.self_position, direction)
        if in_bounds(target, obs.rows, obs.cols) and target not in obs.visible_barriers:
            moves.append((direction, target))
    return moves


def _toward(moves: list[tuple[str, Position]], point: Position) -> tuple[str, Position]:
    return min(moves, key=lambda m: chebyshev(m[1], point))


def _away(moves: list[tuple[str, Position]], point: Position) -> tuple[str, Position]:
    return max(moves, key=lambda m: chebyshev(m[1], point))


def observed_cop_action(obs: Observation) -> Action | None:
    """Cop: step toward a visible thief, else patrol toward the board centre."""
    moves = observed_legal_moves(obs)
    if not moves:
        return None
    if obs.opponent_visible and obs.opponent_position is not None:
        chosen = _toward(moves, obs.opponent_position)
    else:
        chosen = _toward(moves, board_center(obs))
    return Action.move(PlayerRole.COP, chosen[1], chosen[0])


def observed_thief_action(obs: Observation) -> Action | None:
    """Thief: step away from a visible cop, else explore toward the edges."""
    moves = observed_legal_moves(obs)
    if not moves:
        return None
    if obs.opponent_visible and obs.opponent_position is not None:
        chosen = _away(moves, obs.opponent_position)
    else:
        chosen = _away(moves, board_center(obs))
    return Action.move(PlayerRole.THIEF, chosen[1], chosen[0])
