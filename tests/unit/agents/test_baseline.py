"""Unit tests for the deterministic baseline policies."""

from mars777_cop_thief.agents.baseline import (
    chebyshev,
    cop_policy,
    first_legal_action,
    legal_moves,
    thief_policy,
)
from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import ActionType, PlayerRole, Position
from mars777_cop_thief.game.rules import move_violation


def _legal(state, role, action) -> bool:
    origin = state.position_of(role)
    violation = move_violation(origin, action.target, state.rows, state.cols, state.barriers, False)
    return violation is None


def test_cop_steps_toward_thief(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(2, 2))
    action = cop_policy(state)
    assert action.type is ActionType.MOVE
    assert _legal(state, PlayerRole.COP, action)
    assert chebyshev(action.target, state.thief) < chebyshev(state.cop, state.thief)


def test_thief_steps_away_from_cop(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(2, 2))
    action = thief_policy(state)
    assert _legal(state, PlayerRole.THIEF, action)
    assert chebyshev(action.target, state.cop) > chebyshev(state.thief, state.cop)


def test_policies_never_choose_stay(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(2, 2))
    assert cop_policy(state).target != state.cop
    assert thief_policy(state).target != state.thief


def test_cop_uses_first_legal_fallback_when_no_progress(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(2, 2))
    state.barriers.add(Position(1, 1))  # block the only distance-reducing step
    action = cop_policy(state)
    assert action.target == first_legal_action(state, PlayerRole.COP).target
    assert _legal(state, PlayerRole.COP, action)


def test_first_legal_action_none_when_stuck(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    state = engine.new_subgame()
    assert legal_moves(state, PlayerRole.THIEF) == []
    assert first_legal_action(state, PlayerRole.THIEF) is None
    assert thief_policy(state) is None
