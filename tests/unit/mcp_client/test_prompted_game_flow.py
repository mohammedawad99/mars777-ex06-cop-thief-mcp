"""In-memory prompted MCP game flow tests (deterministic, no network)."""

import asyncio
import json

from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.llm.agent import LlmAgent
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.provider import LlmResponse
from mars777_cop_thief.mcp_client.game_report import build_prompted_report
from mars777_cop_thief.mcp_client.prompted_game_flow import (
    run_prompted_full_game,
    run_prompted_sub_game,
)
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server

TOKEN = "dummy"


def _servers(make_config, mcp_config, **overrides):
    cfg = make_config(**overrides)
    return cfg, build_cop_server(cfg, mcp_config), build_thief_server(cfg, mcp_config)


def _full(cfg, cop, thief, n, agent):
    async def go():
        async with Client(cop) as c, Client(thief) as t:
            return await run_prompted_full_game(GameEngine(cfg), n, c, t, agent, TOKEN, TOKEN)

    return asyncio.run(go())


def test_full_game_report_is_serializable_with_token_fields(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config)
    results, acc = _full(cfg, cop, thief, 6, LlmAgent(FakeLocalProvider()))
    report = build_prompted_report(cfg, results, acc, "http://c", "http://t", "fake_local", "v1")
    assert json.dumps(report)
    assert len(results) == 6
    assert report["llm_mode"] == "fake_local"
    assert report["total_prompt_tokens_estimate"] > 0
    assert report["estimated_cost_usd"] >= 0
    assert "parse_failures" in report and "fallbacks_used" in report
    assert report["totals"]["thief"] == sum(r.scores["thief"] for r in results)


def test_no_hidden_coordinate_leak(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config)
    results, _ = _full(cfg, cop, thief, 1, LlmAgent(FakeLocalProvider()))
    report = build_prompted_report(
        cfg,
        results,
        {
            "prompt_tokens": 1,
            "response_tokens": 1,
            "cost": 0.0,
            "parse_failures": 0,
            "fallbacks_used": 0,
        },
        "http://c",
        "http://t",
        "x",
        "y",
    )
    assert report["hidden_state_respected"] is True
    for record in results[0].transcript:
        assert record["audit"]["leaked"] is False


class _BadProvider:
    provider_name = "bad"
    model_name = "bad-v0"

    def complete(self, prompt, *, role, context):
        return LlmResponse("no decision here at all", "bad", "bad-v0", 4, 2, 0.0, {})


class _ScriptedProvider:
    provider_name = "scripted"
    model_name = "scripted-v0"

    def __init__(self, text):
        self._text = text

    def complete(self, prompt, *, role, context):
        return LlmResponse(self._text, "scripted", "scripted-v0", 4, 2, 0.0, {})


def _empty_acc():
    return {
        "prompt_tokens": 0,
        "response_tokens": 0,
        "cost": 0.0,
        "parse_failures": 0,
        "fallbacks_used": 0,
    }


def _sub(cfg, cop, thief, provider, acc, **kw):
    async def go():
        async with Client(cop) as c, Client(thief) as t:
            return await run_prompted_sub_game(
                GameEngine(cfg), c, t, LlmAgent(provider), TOKEN, TOKEN, acc, **kw
            )

    return asyncio.run(go())


def test_unparseable_response_triggers_fallback(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, max_moves=2)
    acc = _empty_acc()
    result = _sub(cfg, cop, thief, _BadProvider(), acc)
    assert result.winner in {"cop", "thief"}
    assert acc["parse_failures"] > 0
    assert acc["fallbacks_used"] > 0


def test_illegal_but_parseable_action_falls_back(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, max_moves=4)
    acc = _empty_acc()
    # Cop starts at (0,0); "move north" is parseable but out of bounds → fallback.
    result = _sub(cfg, cop, thief, _ScriptedProvider("ACTION: move north"), acc)
    assert result.winner in {"cop", "thief"}
    assert acc["fallbacks_used"] > 0
    assert acc["parse_failures"] == 0  # the action parsed fine; it was just illegal


def test_cop_barrier_action_is_applied(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, max_moves=4)
    result = _sub(cfg, cop, thief, _ScriptedProvider("ACTION: barrier south"), _empty_acc())
    assert result.winner in {"cop", "thief"}
    assert result.barriers  # the cop's barrier action reached the engine


def test_stuck_actor_ends_sub_game(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, grid_size=[1, 1])
    result = _sub(cfg, cop, thief, FakeLocalProvider(), _empty_acc())
    assert result.winner == "thief"
    assert result.move_count == 0


def test_illegal_action_with_no_fallback_ends_sub_game(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, grid_size=[1, 1])
    # Parseable but illegal "move north" on a 1x1 board, with no legal fallback.
    result = _sub(cfg, cop, thief, _ScriptedProvider("ACTION: move north"), _empty_acc())
    assert result.winner == "thief"
    assert result.move_count == 0
