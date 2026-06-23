"""Mutable per-sub-game state container.

A ``SubGameState`` is advanced in place by the engine. Whose turn it is follows
directly from ``move_count`` and the configured ``turn_order``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mars777_cop_thief.game.models import PlayerRole, Position


@dataclass
class SubGameState:
    """Authoritative state of a single sub-game."""

    rows: int
    cols: int
    cop: Position
    thief: Position
    max_moves: int
    max_barriers: int
    turn_order: tuple[PlayerRole, ...]
    barriers: set[Position] = field(default_factory=set)
    barriers_placed: int = 0
    move_count: int = 0
    terminal: bool = False
    winner: PlayerRole | None = None

    @property
    def current_role(self) -> PlayerRole:
        """The role expected to act next (thief first by default)."""
        return self.turn_order[self.move_count % len(self.turn_order)]

    def position_of(self, role: PlayerRole) -> Position:
        """Return the current cell of ``role``."""
        return self.cop if role is PlayerRole.COP else self.thief

    def occupied(self) -> set[Position]:
        """Cells currently held by a player (cannot host a barrier)."""
        return {self.cop, self.thief}
