"""Unit tests for log-ready event construction."""

from mars777_cop_thief.game.events import build_event
from mars777_cop_thief.game.models import (
    Action,
    ActionType,
    PlayerRole,
    Position,
    RuleViolation,
)


def test_event_serialises_target_and_outcome():
    action = Action.move(PlayerRole.COP, Position(1, 2), direction="southeast")
    event = build_event(action, True, None, True, True, PlayerRole.COP, 4)
    assert event["role"] == "cop"
    assert event["action"] == "move"
    assert event["target"] == {"row": 1, "col": 2}
    assert event["direction"] == "southeast"
    assert event["winner"] == "cop"
    assert event["move_count"] == 4


def test_event_handles_missing_target_and_violation():
    action = Action(PlayerRole.THIEF, ActionType.MOVE, target=None)
    event = build_event(action, False, RuleViolation.STAY_NOT_ALLOWED, False, False, None, 0)
    assert event["target"] is None
    assert event["violation"] == "stay_not_allowed"
    assert event["winner"] is None
    assert event["ok"] is False
