"""Unit tests for the game smoke entrypoint and SDK delegation (no servers)."""

import asyncio

from mars777_cop_thief.mcp_client import game_smoke
from mars777_cop_thief.sdk import AssignmentSdk


def test_main_returns_zero_on_pass(monkeypatch, capsys):
    monkeypatch.setattr(game_smoke, "run_game_smoke", lambda: {"passed": True, "checks": {}})
    assert game_smoke.main() == 0
    assert "passed" in capsys.readouterr().out


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(game_smoke, "run_game_smoke", lambda: {"passed": False})
    assert game_smoke.main() == 1


def test_play_reports_servers_not_ready(monkeypatch):
    async def never_ready(target):
        return False

    monkeypatch.setattr(game_smoke, "wait_ready", never_ready)
    result = asyncio.run(game_smoke._play({}, "http://a", "http://b", 1))
    assert result["passed"] is False
    assert result["error"] == "servers_not_ready"


def test_sdk_delegates_to_game_smoke(monkeypatch):
    calls = {}

    def fake(num_sub_games=None):
        calls["n"] = num_sub_games
        return {"passed": True, "num_sub_games": num_sub_games}

    monkeypatch.setattr("mars777_cop_thief.sdk.sdk.run_game_smoke", fake)
    sdk = AssignmentSdk()
    assert sdk.run_local_mcp_sub_game()["num_sub_games"] == 1
    assert sdk.run_local_mcp_full_game()["passed"] is True
    assert calls["n"] is None  # full game uses the configured default
