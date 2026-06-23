"""Verify the default game config exists and carries the assignment defaults."""

import json
from pathlib import Path

import pytest

from mars777_cop_thief.shared.config import (
    ConfigError,
    load_game_config,
    load_json_config,
)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "game.default.json"


def test_game_config_file_exists():
    assert CONFIG_PATH.is_file()


def test_game_config_has_assignment_defaults():
    data = load_game_config(CONFIG_PATH)
    assert data["version"] == "1.00"
    assert data["group_code"] == "MaRs-777"
    assert data["group_slug"] == "mars777"
    assert data["grid_size"] == [5, 5]
    assert data["max_moves"] == 25
    assert data["num_sub_games"] == 6
    assert data["scoring"]["cop_win"] == 20
    assert data["scoring"]["thief_win"] == 10
    assert data["timezone"] == "Asia/Jerusalem"
    assert data["allow_stay"] is False
    assert len(data["movement_directions"]) == 8


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_json_config(tmp_path / "nope.json")


def test_invalid_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid", encoding="utf-8")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_json_config(bad)


def test_non_object_root_raises(tmp_path):
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ConfigError, match="must be an object"):
        load_json_config(arr)


def test_missing_required_keys_raises(tmp_path):
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"version": "1.00"}), encoding="utf-8")
    with pytest.raises(ConfigError, match="Missing required"):
        load_game_config(partial)
