"""Unit tests for the GameEngine action application and scoring."""

import pytest

from mars777_cop_thief.game import (
    Action,
    ActionType,
    GameEngine,
    PlayerRole,
    Position,
    RuleViolation,
)


@pytest.mark.parametrize("size", [2, 3, 4, 5])
def test_engine_runs_on_sanity_grid_sizes(make_config, size):
    engine = GameEngine(make_config(grid_size=[size, size]))
    state = engine.new_subgame()
    assert state.cop == Position(0, 0)
    assert state.thief == Position(size - 1, size - 1)
    result = engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(size - 2, size - 1)))
    assert result.ok
    assert state.current_role is PlayerRole.COP


def test_thief_moves_first(engine):
    state = engine.new_subgame()
    assert state.current_role is PlayerRole.THIEF


def test_wrong_player_turn_rejected(engine):
    state = engine.new_subgame()
    result = engine.apply_action(state, Action.move(PlayerRole.COP, Position(0, 1)))
    assert not result.ok
    assert result.violation is RuleViolation.WRONG_TURN
    assert state.move_count == 0


def test_turn_alternates_to_cop_after_thief(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    assert state.current_role is PlayerRole.COP


def test_cop_places_barrier(engine):
    state = engine.new_subgame()
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    result = engine.apply_action(state, Action.barrier(Position(2, 2)))
    assert result.ok
    assert Position(2, 2) in state.barriers
    assert state.barriers_placed == 1


def test_cop_cannot_exceed_max_barriers(make_config):
    engine = GameEngine(make_config(max_barriers=1))
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    assert engine.apply_action(state, Action.barrier(Position(2, 2))).ok
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 3)))
    second = engine.apply_action(state, Action.barrier(Position(2, 3)))
    assert not second.ok
    assert second.violation is RuleViolation.BARRIER_LIMIT_REACHED


def test_thief_cannot_place_barrier(engine):
    state = engine.new_subgame()
    thief_barrier = Action(PlayerRole.THIEF, ActionType.PLACE_BARRIER, Position(1, 1))
    result = engine.apply_action(state, thief_barrier)
    assert not result.ok
    assert result.violation is RuleViolation.THIEF_CANNOT_PLACE_BARRIER


def test_barrier_cannot_sit_on_occupied_cell(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    result = engine.apply_action(state, Action.barrier(Position(0, 0)))
    assert not result.ok
    assert result.violation is RuleViolation.BARRIER_ON_OCCUPIED


def test_barrier_cannot_be_placed_twice(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    engine.apply_action(state, Action.barrier(Position(2, 2)))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 3)))
    repeat = engine.apply_action(state, Action.barrier(Position(2, 2)))
    assert not repeat.ok
    assert repeat.violation is RuleViolation.BARRIER_EXISTS


def test_cop_captures_thief_by_moving_onto_it(engine):
    state = engine.new_subgame(cop=Position(2, 2), thief=Position(2, 3))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(1, 3)))
    result = engine.apply_action(state, Action.move(PlayerRole.COP, Position(1, 3)))
    assert result.captured
    assert result.terminal
    assert result.winner is PlayerRole.COP


def test_thief_moving_onto_cop_is_capture(engine):
    state = engine.new_subgame(cop=Position(1, 1), thief=Position(2, 2))
    result = engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(1, 1)))
    assert result.captured
    assert result.winner is PlayerRole.COP


def test_thief_wins_when_max_moves_reached(make_config):
    engine = GameEngine(make_config(max_moves=2))
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    result = engine.apply_action(state, Action.move(PlayerRole.COP, Position(1, 1)))
    assert result.terminal
    assert result.winner is PlayerRole.THIEF


def test_action_after_terminal_is_rejected(make_config):
    engine = GameEngine(make_config())
    state = engine.new_subgame(cop=Position(1, 1), thief=Position(2, 2))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(1, 1)))
    blocked = engine.apply_action(state, Action.move(PlayerRole.COP, Position(0, 0)))
    assert not blocked.ok
    assert blocked.violation is RuleViolation.GAME_OVER


def test_illegal_move_keeps_engine_usable(engine):
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(0, 0))
    bad = engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(0, 2)))
    assert not bad.ok
    assert state.move_count == 0
    good = engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(0, 1)))
    assert good.ok


def test_scoring_for_cop_win(engine):
    state = engine.new_subgame(cop=Position(1, 1), thief=Position(2, 2))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(1, 1)))
    assert engine.score_state(state) == {"cop": 20, "thief": 5}


def test_scoring_for_thief_win(make_config):
    engine = GameEngine(make_config(max_moves=2))
    state = engine.new_subgame(cop=Position(0, 0), thief=Position(4, 4))
    engine.apply_action(state, Action.move(PlayerRole.THIEF, Position(3, 4)))
    engine.apply_action(state, Action.move(PlayerRole.COP, Position(1, 1)))
    assert engine.score_state(state) == {"cop": 5, "thief": 10}


def test_scoring_non_terminal_is_zero(engine):
    state = engine.new_subgame()
    assert engine.score_state(state) == {"cop": 0, "thief": 0}
