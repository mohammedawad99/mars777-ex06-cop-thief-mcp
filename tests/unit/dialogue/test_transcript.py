"""Unit tests for transcript records and audit isolation."""

from mars777_cop_thief.dialogue.messages import compose_message
from mars777_cop_thief.dialogue.transcript import audit_facts, make_message_event
from mars777_cop_thief.game.models import PlayerRole, Position
from mars777_cop_thief.observability.observation import observe


def test_message_event_has_required_fields(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    obs = observe(state, PlayerRole.COP, 1)
    text = compose_message(obs)
    event = make_message_event(
        3, PlayerRole.COP, PlayerRole.THIEF, text, obs.opponent_visible, audit_facts(obs)
    )
    assert event["turn_index"] == 3
    assert event["sender"] == "cop"
    assert event["recipient"] == "thief"
    assert event["message"] == text
    assert event["opponent_visible"] is True


def test_audit_is_separate_from_message_text(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    obs = observe(state, PlayerRole.COP, 1)
    event = make_message_event(
        0, PlayerRole.COP, PlayerRole.THIEF, compose_message(obs), True, audit_facts(obs)
    )
    assert isinstance(event["audit"], dict)
    # Audit keys/metadata must not appear inside the readable message text.
    assert "opponent_visible" not in event["message"]
    assert "self_position" not in event["message"]
    assert "relative_direction" not in event["message"]


def test_audit_does_not_carry_hidden_opponent_coordinates(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    audit = audit_facts(observe(state, PlayerRole.COP, 1))
    assert audit["opponent_visible"] is False
    assert audit["relative_direction"] is None
    assert "opponent_position" not in audit
