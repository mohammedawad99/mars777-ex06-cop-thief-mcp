"""Unit tests for the MCP-backed report builder."""

import asyncio
import json

from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.mcp_client.game_flow import run_mcp_full_game
from mars777_cop_thief.mcp_client.game_report import _any_leak, build_mcp_report
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server

COP_URL = "http://127.0.0.1:8001/mcp"
THIEF_URL = "http://127.0.0.1:8002/mcp"
TOK = "zzz-secret-token-zzz"


class _Result:
    def __init__(self, transcript):
        self.transcript = transcript


def test_any_leak_detects_and_clears():
    assert _any_leak([_Result([{"audit": {"leaked": True}}])]) is True
    assert _any_leak([_Result([{"audit": {"leaked": False}}])]) is False
    assert _any_leak([]) is False


def _two_sub_games(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOK)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOK)
    cfg = make_config(grid_size=[2, 2])
    cop = build_cop_server(cfg, mcp_config)
    thief = build_thief_server(cfg, mcp_config)

    async def go():
        async with Client(cop) as c, Client(thief) as t:
            return await run_mcp_full_game(GameEngine(cfg), 2, c, t, TOK, TOK)

    return cfg, asyncio.run(go())


def test_report_has_local_status_fields(make_config, mcp_config, monkeypatch):
    cfg, results = _two_sub_games(make_config, mcp_config, monkeypatch)
    report = build_mcp_report(cfg, results, COP_URL, THIEF_URL)
    assert report["transport"] == "local_mcp_http"
    assert report["mcp_status"] == "local_verified"
    assert report["cop_mcp_url"] == COP_URL
    assert report["thief_mcp_url"] == THIEF_URL
    assert report["cloud_status"] == "not_deployed"
    assert report["email_status"] == "not_sent"
    assert report["hidden_state_respected"] is True


def test_report_is_json_serializable_with_totals(make_config, mcp_config, monkeypatch):
    cfg, results = _two_sub_games(make_config, mcp_config, monkeypatch)
    report = build_mcp_report(cfg, results, COP_URL, THIEF_URL)
    assert json.dumps(report)
    assert len(report["sub_games"]) == 2
    assert report["totals"]["cop"] == sum(r.scores["cop"] for r in results)
    assert report["totals"]["thief"] == sum(r.scores["thief"] for r in results)


def test_report_omits_tokens(make_config, mcp_config, monkeypatch):
    cfg, results = _two_sub_games(make_config, mcp_config, monkeypatch)
    serialized = json.dumps(build_mcp_report(cfg, results, COP_URL, THIEF_URL))
    assert TOK not in serialized  # the auth token never reaches the report
    assert "auth_token" not in serialized
