"""Unit tests for partial observations and hidden-coordinate isolation."""

import json

from mars777_cop_thief.game.models import PlayerRole, Position
from mars777_cop_thief.observability.observation import observe


def test_opponent_visible_within_radius(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    obs = observe(state, PlayerRole.COP, 1)
    assert obs.opponent_visible
    assert obs.opponent_position == Position(2, 3)


def test_opponent_hidden_outside_radius(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    obs = observe(state, PlayerRole.COP, 1)
    assert not obs.opponent_visible
    assert obs.opponent_position is None


def test_hidden_opponent_coordinates_not_exposed(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    obs = observe(state, PlayerRole.COP, 1)
    text = json.dumps(obs.to_dict())
    # The thief sits at row/col 4; that coordinate must not appear anywhere.
    assert '"row": 4' not in text
    assert '"col": 4' not in text
    assert obs.to_dict()["opponent_position"] is None


def test_agent_always_knows_self_and_board(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    obs = observe(state, PlayerRole.THIEF, 1)
    assert obs.self_position == Position(4, 4)
    assert obs.rows == 5 and obs.cols == 5
    assert obs.max_moves == 25


def test_cop_observation_includes_barrier_budget(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    cop_obs = observe(state, PlayerRole.COP, 1)
    thief_obs = observe(state, PlayerRole.THIEF, 1)
    assert cop_obs.barrier_budget == 5
    assert thief_obs.barrier_budget is None
