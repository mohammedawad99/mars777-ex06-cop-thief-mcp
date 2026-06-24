"""Unit tests for the smoke entrypoint and readiness branch (no real servers)."""

import asyncio

from mars777_cop_thief.mcp_client import smoke


def test_main_returns_zero_on_pass(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "run_smoke", lambda: {"passed": True, "checks": {}})
    assert smoke.main() == 0
    assert "passed" in capsys.readouterr().out


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(smoke, "run_smoke", lambda: {"passed": False})
    assert smoke.main() == 1


def test_drive_reports_not_ready(monkeypatch):
    async def never_ready(target):
        return False

    monkeypatch.setattr(smoke, "wait_ready", never_ready)
    result = asyncio.run(smoke._drive("http://a", "http://b"))
    assert result["passed"] is False
    assert result["error"] == "servers_not_ready"
