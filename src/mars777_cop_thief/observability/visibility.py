"""Chebyshev visibility helpers for partial observability.

Visibility uses Chebyshev (king-move) distance to match 8-direction movement.
``relative_direction`` yields a qualitative compass word only — never numeric
coordinates.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import Position


def chebyshev(a: Position, b: Position) -> int:
    """King-move distance between two cells."""
    return max(abs(a.row - b.row), abs(a.col - b.col))


def is_visible(observer: Position, target: Position, radius: int) -> bool:
    """True if ``target`` is within Chebyshev ``radius`` of ``observer``."""
    return chebyshev(observer, target) <= radius


_VERTICAL = {-1: "north", 0: "", 1: "south"}
_HORIZONTAL = {-1: "west", 0: "", 1: "east"}


def relative_direction(observer: Position, target: Position) -> str | None:
    """Qualitative compass word from observer to target (None if same cell)."""
    drow = (target.row > observer.row) - (target.row < observer.row)
    dcol = (target.col > observer.col) - (target.col < observer.col)
    if drow == 0 and dcol == 0:
        return None
    vertical, horizontal = _VERTICAL[drow], _HORIZONTAL[dcol]
    if vertical and horizontal:
        return f"{vertical}-{horizontal}"
    return vertical or horizontal
