"""The SDK runs local self-play end-to-end from the default config file."""

import json
from pathlib import Path

from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.sdk import AssignmentSdk

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "game.default.json"


def test_sdk_runs_local_full_game_and_report_serializes():
    report = AssignmentSdk().run_local_full_game(CONFIG_PATH)
    assert json.dumps(report)
    assert len(report["sub_games"]) == 6
    assert report["config"]["num_sub_games"] == 6
    assert report["mcp_status"] == "not-deployed"


def test_sdk_runs_local_sub_game():
    result = AssignmentSdk().run_local_sub_game(CONFIG_PATH)
    assert isinstance(result, SubGameResult)
    assert result.winner in {"cop", "thief"}
    assert result.events
