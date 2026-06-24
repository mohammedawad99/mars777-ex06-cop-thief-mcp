"""Unit tests for the live-gated Gemini smoke (no network, no key)."""

import json
from types import SimpleNamespace

from mars777_cop_thief.mcp_client import gemini_prompted_smoke as smoke


def test_skips_when_not_enabled():
    result = smoke.run_gemini_smoke(env={})
    assert result["status"] == "skipped"
    assert result["passed"] is True
    assert "RUN_GEMINI_LIVE" in result["reason"]


def test_errors_when_enabled_without_key():
    result = smoke.run_gemini_smoke(env={"RUN_GEMINI_LIVE": "1"})
    assert result["status"] == "error"
    assert result["passed"] is False
    assert "no API key" in result["reason"]


def test_main_skips_cleanly_with_exit_zero(monkeypatch, capsys):
    monkeypatch.delenv("RUN_GEMINI_LIVE", raising=False)
    assert smoke.main() == 0
    assert "skipped" in capsys.readouterr().out


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(smoke, "run_gemini_smoke", lambda: {"passed": False, "status": "error"})
    assert smoke.main() == 1


def test_summary_shape_has_no_key():
    provider = SimpleNamespace(provider_name="gemini", model_name="gemini-2.5-flash")
    result = SimpleNamespace(winner="thief", move_count=4)
    acc = {
        "parse_failures": 0,
        "fallbacks_used": 1,
        "prompt_tokens": 50,
        "response_tokens": 8,
        "cost": 0.0,
    }
    summary = smoke._summary(provider, [result], acc)
    assert summary["status"] == "ran"
    assert summary["llm_mode"] == "gemini"
    assert summary["model_name"] == "gemini-2.5-flash"
    assert summary["total_prompt_tokens_estimate"] == 50
    assert "api_key" not in json.dumps(summary).lower()
