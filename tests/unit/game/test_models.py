"""Unit tests for the pure game-domain models."""

from mars777_cop_thief.game.models import (
    DIRECTION_DELTAS,
    Action,
    ActionType,
    PlayerRole,
    Position,
)


def test_position_equality_and_hashing():
    assert Position(1, 2) == Position(1, 2)
    assert Position(1, 2) != Position(2, 1)
    assert len({Position(0, 0), Position(0, 0)}) == 1


def test_eight_directions_are_defined():
    assert len(DIRECTION_DELTAS) == 8
    for drow, dcol in DIRECTION_DELTAS.values():
        assert max(abs(drow), abs(dcol)) == 1


def test_move_action_factory():
    action = Action.move(PlayerRole.THIEF, Position(0, 1), direction="east")
    assert action.role is PlayerRole.THIEF
    assert action.type is ActionType.MOVE
    assert action.target == Position(0, 1)
    assert action.direction == "east"


def test_barrier_action_is_always_cop():
    action = Action.barrier(Position(2, 2))
    assert action.role is PlayerRole.COP
    assert action.type is ActionType.PLACE_BARRIER
    assert action.target == Position(2, 2)
