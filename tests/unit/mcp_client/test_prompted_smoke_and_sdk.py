"""Unit tests for the prompted smoke entrypoint and SDK delegation (no servers)."""

import asyncio

from mars777_cop_thief.mcp_client import prompted_game_smoke as smoke
from mars777_cop_thief.sdk import AssignmentSdk


def test_main_returns_zero_on_pass(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "run_prompted_game_smoke", lambda: {"passed": True, "checks": {}})
    assert smoke.main() == 0
    assert "passed" in capsys.readouterr().out


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(smoke, "run_prompted_game_smoke", lambda: {"passed": False})
    assert smoke.main() == 1


def test_play_reports_servers_not_ready(monkeypatch):
    async def never_ready(target):
        return False

    monkeypatch.setattr(smoke, "wait_ready", never_ready)
    result = asyncio.run(smoke._play({}, "http://a", "http://b", 1))
    assert result["passed"] is False
    assert result["error"] == "servers_not_ready"


def test_sdk_delegates_to_prompted_smoke(monkeypatch):
    monkeypatch.setattr(
        "mars777_cop_thief.sdk.sdk.run_prompted_game_smoke",
        lambda num_sub_games=None: {"passed": True, "n": num_sub_games},
    )
    assert AssignmentSdk().run_local_prompted_mcp_game(num_sub_games=1)["n"] == 1
