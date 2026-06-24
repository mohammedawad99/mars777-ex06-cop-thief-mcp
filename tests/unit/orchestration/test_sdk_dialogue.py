"""The SDK runs local observed/dialogue self-play from the default config file."""

import json
from pathlib import Path

from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.sdk import AssignmentSdk

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "game.default.json"


def test_sdk_runs_dialogue_full_game_and_report_serializes():
    report = AssignmentSdk().run_local_dialogue_full_game(CONFIG_PATH)
    assert json.dumps(report)
    assert report["mode"] == "observed-dialogue"
    assert len(report["sub_games"]) == 6
    assert report["sub_games"][0]["transcript"]
    assert report["mcp_status"] == "not-deployed"


def test_sdk_runs_dialogue_sub_game():
    result = AssignmentSdk().run_local_dialogue_sub_game(CONFIG_PATH)
    assert isinstance(result, SubGameResult)
    assert result.winner in {"cop", "thief"}
    assert result.transcript
