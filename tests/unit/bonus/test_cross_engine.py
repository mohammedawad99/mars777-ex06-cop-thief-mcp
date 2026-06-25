"""Unit tests for the official bonus rules + canonical engine config (no IO)."""

from mars777_cop_thief.bonus.cross_engine import (
    DEFAULT_COP_START,
    DEFAULT_THIEF_START,
    OFFICIAL_RULES,
    bonus_engine,
    outcome_reason,
)
from mars777_cop_thief.game.models import PlayerRole, Position


def test_official_rules_match_agreement():
    assert OFFICIAL_RULES["board_size"] == [8, 8]
    assert OFFICIAL_RULES["turn_order"] == ["thief", "cop"]
    assert OFFICIAL_RULES["num_sub_games"] == 6
    assert OFFICIAL_RULES["max_moves"] == 25
    assert OFFICIAL_RULES["max_barriers"] == 5
    assert OFFICIAL_RULES["barriers_role"] == "cop"
    assert OFFICIAL_RULES["diagonal_movement"] is True
    assert DEFAULT_COP_START == [0, 0] and DEFAULT_THIEF_START == [7, 7]


def test_bonus_engine_is_8x8_thief_first_and_scores():
    engine = bonus_engine()
    assert (engine.rows, engine.cols) == (8, 8)
    assert engine.max_moves == 25 and engine.max_barriers == 5
    assert engine.turn_order[0] is PlayerRole.THIEF
    state = engine.new_subgame(Position(0, 0), Position(7, 7))
    assert state.current_role is PlayerRole.THIEF
    state.winner = PlayerRole.COP
    assert engine.score_state(state) == {"cop": 20, "thief": 5}
    state.winner = PlayerRole.THIEF
    assert engine.score_state(state) == {"cop": 5, "thief": 10}


def test_outcome_reason():
    assert outcome_reason("cop", 7, 25) == "capture"
    assert outcome_reason("thief", 25, 25) == "thief_survived_max_moves"
    assert outcome_reason("thief", 10, 25) == "thief_survived"
    assert outcome_reason(None, 3, 25) == "undecided"
