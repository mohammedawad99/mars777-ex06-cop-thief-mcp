"""Pure game-domain value types: positions, roles, actions, and results.

These types are deliberately free of behaviour and external dependencies so the
engine, future MCP servers, and tests share one vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class Position:
    """Zero-based board coordinate (row, col); north decreases ``row``."""

    row: int
    col: int


class PlayerRole(StrEnum):
    """The two players in a sub-game."""

    THIEF = "thief"
    COP = "cop"


class ActionType(StrEnum):
    """What a player attempts on its turn."""

    MOVE = "move"
    PLACE_BARRIER = "place_barrier"


class RuleViolation(StrEnum):
    """Structured reason an action was rejected (never raised in game flow)."""

    GAME_OVER = "game_over"
    WRONG_TURN = "wrong_turn"
    UNKNOWN_DIRECTION = "unknown_direction"
    NOT_ONE_STEP = "not_one_step"
    STAY_NOT_ALLOWED = "stay_not_allowed"
    OUT_OF_BOUNDS = "out_of_bounds"
    INTO_BARRIER = "into_barrier"
    THIEF_CANNOT_PLACE_BARRIER = "thief_cannot_place_barrier"
    BARRIER_LIMIT_REACHED = "barrier_limit_reached"
    BARRIER_OUT_OF_BOUNDS = "barrier_out_of_bounds"
    BARRIER_ON_OCCUPIED = "barrier_on_occupied"
    BARRIER_EXISTS = "barrier_exists"


# Compass direction deltas in (drow, dcol); the eight legal one-step moves.
DIRECTION_DELTAS: dict[str, tuple[int, int]] = {
    "north": (-1, 0),
    "south": (1, 0),
    "east": (0, 1),
    "west": (0, -1),
    "northeast": (-1, 1),
    "northwest": (-1, -1),
    "southeast": (1, 1),
    "southwest": (1, -1),
}


@dataclass(frozen=True)
class Action:
    """An attempted action; ``target`` is the destination/barrier cell."""

    role: PlayerRole
    type: ActionType
    target: Position | None = None
    direction: str | None = None

    @classmethod
    def move(cls, role: PlayerRole, target: Position, direction: str | None = None) -> Action:
        """Build a MOVE action to ``target`` (direction kept for the log)."""
        return cls(role=role, type=ActionType.MOVE, target=target, direction=direction)

    @classmethod
    def barrier(cls, target: Position) -> Action:
        """Build a cop PLACE_BARRIER action on ``target``."""
        return cls(role=PlayerRole.COP, type=ActionType.PLACE_BARRIER, target=target)


@dataclass(frozen=True)
class ActionResult:
    """Outcome of applying an action, including a log-ready ``event`` dict."""

    ok: bool
    role: PlayerRole
    action: ActionType
    violation: RuleViolation | None = None
    captured: bool = False
    terminal: bool = False
    winner: PlayerRole | None = None
    event: dict | None = None
