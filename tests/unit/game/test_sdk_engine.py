"""The SDK can build a working engine from the default config file."""

from pathlib import Path

from mars777_cop_thief.game import GameEngine, PlayerRole
from mars777_cop_thief.sdk import AssignmentSdk

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "game.default.json"


def test_sdk_creates_engine_from_default_config():
    engine = AssignmentSdk().create_game_engine(CONFIG_PATH)
    assert isinstance(engine, GameEngine)
    assert engine.rows == 5
    assert engine.cols == 5
    assert engine.max_moves == 25
    assert engine.max_barriers == 5
    assert engine.turn_order == (PlayerRole.THIEF, PlayerRole.COP)


def test_engine_from_sdk_runs_a_first_turn():
    engine = AssignmentSdk().create_game_engine(CONFIG_PATH)
    state = engine.new_subgame()
    assert state.current_role is PlayerRole.THIEF
    assert not state.terminal
