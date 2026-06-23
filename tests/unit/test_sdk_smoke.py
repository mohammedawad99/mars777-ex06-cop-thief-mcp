"""Smoke test: the SDK façade loads version and the default config."""

from pathlib import Path

from mars777_cop_thief.sdk import AssignmentSdk

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "game.default.json"


def test_sdk_reports_version():
    sdk = AssignmentSdk()
    assert sdk.get_version() == "1.00"


def test_sdk_loads_default_config():
    sdk = AssignmentSdk()
    data = sdk.load_game_config(CONFIG_PATH)
    assert data["group_code"] == "MaRs-777"
    assert data["num_sub_games"] == 6
