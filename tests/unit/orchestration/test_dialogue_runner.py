"""Unit tests for the local observed/dialogue runner."""

import json

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.orchestration.dialogue_runner import (
    run_dialogue_full_game,
    run_dialogue_sub_game,
)

MESSAGE_KEYS = {"turn_index", "sender", "recipient", "message", "opponent_visible", "audit"}


def test_runner_records_action_and_message_events(engine):
    result = run_dialogue_sub_game(engine, radius=1)
    assert result.events
    assert result.transcript
    assert len(result.events) >= len(result.transcript)
    for record in result.transcript:
        assert MESSAGE_KEYS <= set(record)


def test_runner_stops_on_capture(make_config):
    engine = GameEngine(make_config(grid_size=[2, 2]))
    result = run_dialogue_sub_game(engine, radius=1)
    assert result.winner == "cop"
    assert any(event["captured"] for event in result.events)


def test_runner_stops_at_max_moves_with_thief_win(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=2))
    result = run_dialogue_sub_game(engine, radius=1)
    assert result.winner == "thief"
    assert result.move_count == 2


def test_dialogue_result_is_json_serializable(engine):
    result = run_dialogue_sub_game(engine, radius=1)
    assert json.dumps(result.to_dict())
    assert result.to_dict()["transcript"]


def test_full_game_runs_six_dialogue_sub_games(engine):
    results = run_dialogue_full_game(engine, 6, radius=1)
    assert len(results) == 6
    assert all(r.transcript for r in results)


def test_illegal_observed_action_is_recorded_and_falls_back(make_config):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=4))

    def bad_cop(obs):
        return Action.move(PlayerRole.COP, Position(-1, -1))  # always out of bounds

    result = run_dialogue_sub_game(engine, radius=1, cop_policy=bad_cop)
    assert any(not event["ok"] for event in result.events)
    assert result.winner in {"cop", "thief"}


def test_stuck_actor_ends_dialogue_sub_game(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    result = run_dialogue_sub_game(engine, radius=1)
    assert result.winner == "thief"
    assert result.move_count == 0
    assert len(result.transcript) == 1
    assert result.events[0]["ok"] is False
