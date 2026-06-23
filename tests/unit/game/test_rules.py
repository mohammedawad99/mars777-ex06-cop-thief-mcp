"""Unit tests for the pure rule predicates."""

from mars777_cop_thief.game.models import DIRECTION_DELTAS, Position, RuleViolation
from mars777_cop_thief.game.rules import (
    barrier_violation,
    in_bounds,
    move_violation,
    step_target,
)

CENTER = Position(2, 2)


def test_in_bounds_detects_edges():
    assert in_bounds(Position(0, 0), 5, 5)
    assert in_bounds(Position(4, 4), 5, 5)
    assert not in_bounds(Position(-1, 0), 5, 5)
    assert not in_bounds(Position(0, 5), 5, 5)


def test_all_eight_directions_accepted():
    for direction in DIRECTION_DELTAS:
        target = step_target(CENTER, direction)
        assert move_violation(CENTER, target, 5, 5, set(), allow_stay=False) is None


def test_unknown_direction_has_no_target():
    assert step_target(CENTER, "up") is None


def test_stay_rejected_in_baseline():
    assert move_violation(CENTER, CENTER, 5, 5, set(), allow_stay=False) is (
        RuleViolation.STAY_NOT_ALLOWED
    )
    assert move_violation(CENTER, CENTER, 5, 5, set(), allow_stay=True) is None


def test_two_cell_move_rejected():
    target = Position(2, 4)
    assert move_violation(CENTER, target, 5, 5, set(), allow_stay=False) is (
        RuleViolation.NOT_ONE_STEP
    )


def test_move_outside_board_rejected():
    origin = Position(0, 0)
    assert move_violation(origin, Position(-1, 0), 5, 5, set(), allow_stay=False) is (
        RuleViolation.OUT_OF_BOUNDS
    )


def test_move_into_barrier_rejected():
    target = Position(2, 3)
    assert move_violation(CENTER, target, 5, 5, {target}, allow_stay=False) is (
        RuleViolation.INTO_BARRIER
    )


def test_barrier_outside_board_rejected():
    assert barrier_violation(Position(5, 5), 5, 5, set(), set()) is (
        RuleViolation.BARRIER_OUT_OF_BOUNDS
    )


def test_barrier_on_occupied_rejected():
    occupied = {Position(1, 1)}
    assert barrier_violation(Position(1, 1), 5, 5, set(), occupied) is (
        RuleViolation.BARRIER_ON_OCCUPIED
    )


def test_barrier_on_existing_barrier_rejected():
    assert barrier_violation(Position(3, 3), 5, 5, {Position(3, 3)}, set()) is (
        RuleViolation.BARRIER_EXISTS
    )


def test_legal_barrier_allowed():
    assert barrier_violation(Position(3, 3), 5, 5, set(), set()) is None
