"""Unit tests for natural-language message generation."""

from mars777_cop_thief.dialogue.messages import compose_message
from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import PlayerRole, Position
from mars777_cop_thief.observability.observation import observe


def test_message_is_plain_string_not_json(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    message = compose_message(observe(state, PlayerRole.COP, 1))
    assert isinstance(message, str)
    assert not message.lstrip().startswith(("{", "["))


def test_visible_message_uses_qualitative_direction(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    message = compose_message(observe(state, PlayerRole.COP, 1))
    assert "seems close to the" in message
    assert "east" in message
    assert not any(ch.isdigit() for ch in message)  # no exact coordinates


def test_hidden_message_omits_coordinates(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    cop_message = compose_message(observe(state, PlayerRole.COP, 1))
    thief_message = compose_message(observe(state, PlayerRole.THIEF, 1))
    assert "cannot see the thief" in cop_message
    assert "cannot see the cop" in thief_message
    assert not any(ch.isdigit() for ch in cop_message + thief_message)


def test_same_cell_visible_message(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    state = engine.new_subgame()
    message = compose_message(observe(state, PlayerRole.COP, 1))
    assert "right on top of me" in message
