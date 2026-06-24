"""Unit tests for observation-based policies (no hidden-state cheating)."""

from mars777_cop_thief.agents.observed import (
    board_center,
    observed_cop_action,
    observed_thief_action,
)
from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import PlayerRole, Position
from mars777_cop_thief.observability.observation import observe
from mars777_cop_thief.observability.visibility import chebyshev


def test_observed_cop_steps_toward_visible_thief(engine):
    state = engine.new_subgame(cop=Position(0, 3), thief=Position(0, 4))
    action = observed_cop_action(observe(state, PlayerRole.COP, 1))
    assert action.target == Position(0, 4)  # steps onto the visible thief


def test_observed_cop_patrols_centre_when_thief_hidden(engine):
    # Thief at (0,4) is hidden (distance 4); centre is (2,2).
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(0, 4))
    obs = observe(state, PlayerRole.COP, 1)
    assert not obs.opponent_visible
    action = observed_cop_action(obs)
    # Patrols toward centre (south-east → (1,1)), NOT toward the hidden thief (east).
    assert action.target == Position(1, 1)
    assert action.target != Position(0, 1)


def test_observed_thief_steps_away_from_visible_cop(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    obs = observe(state, PlayerRole.THIEF, 1)
    action = observed_thief_action(obs)
    assert chebyshev(action.target, Position(2, 2)) > chebyshev(Position(2, 3), Position(2, 2))


def test_observed_thief_explores_when_cop_hidden(engine):
    # Cop at (4,4) is hidden from thief at (1,1); centre is (2,2).
    state = engine.new_subgame(cop=Position(4, 4), thief=Position(1, 1))
    obs = observe(state, PlayerRole.THIEF, 1)
    assert not obs.opponent_visible
    action = observed_thief_action(obs)
    center = board_center(obs)
    assert chebyshev(action.target, center) > chebyshev(Position(1, 1), center)
    assert action.target != Position(2, 2)  # not toward the hidden cop


def test_observed_policies_return_none_when_stuck(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    state = engine.new_subgame()
    assert observed_cop_action(observe(state, PlayerRole.COP, 1)) is None
    assert observed_thief_action(observe(state, PlayerRole.THIEF, 1)) is None
