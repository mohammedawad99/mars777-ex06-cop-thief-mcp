"""Unit tests for the local self-play runners."""

import pytest

from mars777_cop_thief.agents import cop_policy, thief_policy
from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.orchestration.runner import run_full_game, run_sub_game
from mars777_cop_thief.orchestration.totals import total_scores

EVENT_KEYS = {"turn_index", "actor", "action", "ok", "captured", "winner", "before", "after"}


def test_sub_game_stops_on_cop_capture(make_config):
    engine = GameEngine(make_config(grid_size=[2, 2]))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert result.winner == "cop"
    assert any(event["captured"] for event in result.events)


def test_sub_game_stops_at_max_moves_with_thief_win(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=2))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert result.winner == "thief"
    assert result.move_count == 2


def test_sub_game_result_has_required_fields(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=2))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert result.scores.keys() == {"cop", "thief"}
    assert isinstance(result.cop_final, Position)
    assert isinstance(result.thief_final, Position)
    assert result.move_count == 2
    assert result.events


def test_every_attempt_creates_a_structured_event(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=4))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert len(result.events) == result.move_count
    for index, event in enumerate(result.events):
        assert EVENT_KEYS <= set(event)
        assert event["turn_index"] == index


def test_full_game_runs_six_sub_games(engine):
    results = run_full_game(engine, 6, cop_policy, thief_policy)
    assert len(results) == 6


def test_totals_equal_sum_of_sub_game_scores(engine):
    results = run_full_game(engine, 6, cop_policy, thief_policy)
    totals = total_scores(results)
    assert totals["cop"] == sum(r.scores["cop"] for r in results)
    assert totals["thief"] == sum(r.scores["thief"] for r in results)


@pytest.mark.parametrize("size", [2, 3, 4, 5])
def test_sanity_grid_sizes_run(make_config, size):
    engine = GameEngine(make_config(grid_size=[size, size], max_moves=10))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert result.winner in {"cop", "thief"}
    assert result.rows == size and result.cols == size


def test_illegal_policy_action_is_recorded_and_falls_back(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=4))

    def bad_thief(state):
        return Action.move(PlayerRole.THIEF, Position(-1, -1))  # always out of bounds

    result = run_sub_game(engine, cop_policy, bad_thief)
    assert any(not event["ok"] for event in result.events)
    assert result.winner in {"cop", "thief"}
    assert result.move_count > 0


def test_stuck_actor_ends_sub_game_as_thief_survival(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    result = run_sub_game(engine, cop_policy, thief_policy)
    assert result.winner == "thief"
    assert result.move_count == 0
    assert result.events and result.events[0]["ok"] is False
