"""Unit tests for Chebyshev visibility helpers."""

from mars777_cop_thief.game.models import Position
from mars777_cop_thief.observability.visibility import (
    chebyshev,
    is_visible,
    relative_direction,
)


def test_visible_within_radius():
    assert is_visible(Position(2, 2), Position(2, 3), 1)
    assert is_visible(Position(2, 2), Position(3, 3), 1)


def test_hidden_outside_radius():
    assert not is_visible(Position(0, 0), Position(2, 0), 1)
    assert not is_visible(Position(0, 0), Position(4, 4), 1)


def test_chebyshev_uses_king_move_distance():
    assert chebyshev(Position(0, 0), Position(2, 1)) == 2


def test_relative_direction_words():
    assert relative_direction(Position(2, 2), Position(0, 2)) == "north"
    assert relative_direction(Position(2, 2), Position(2, 4)) == "east"
    assert relative_direction(Position(2, 2), Position(4, 4)) == "south-east"
    assert relative_direction(Position(2, 2), Position(2, 2)) is None
