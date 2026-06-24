"""Unit tests for the MCP server builders and tool adapters (no network)."""

import asyncio

from mars777_cop_thief.mcp_servers.common import server_http_settings
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server, cop_tool_adapters
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server, thief_tool_adapters

ENV_COP = "COP_MCP_TOKEN"
TOKEN = "local-secret"


def _tool_names(server) -> set[str]:
    return {tool.name for tool in asyncio.run(server.list_tools())}


def test_cop_server_registers_expected_tools(make_config, mcp_config):
    names = _tool_names(build_cop_server(make_config(), mcp_config))
    assert {
        "get_role_info",
        "get_observation",
        "propose_action",
        "place_barrier_candidate",
    } <= names


def test_thief_server_omits_barrier_placement(make_config, mcp_config):
    names = _tool_names(build_thief_server(make_config(), mcp_config))
    assert "place_barrier_candidate" not in names
    assert {"get_role_info", "get_observation", "propose_action"} <= names


def test_thief_adapters_have_no_barrier_tool(make_config, mcp_config):
    adapters = thief_tool_adapters(make_config(), mcp_config)
    assert "place_barrier_candidate" not in adapters


def test_cop_adapters_callable_without_network(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv(ENV_COP, TOKEN)
    adapters = cop_tool_adapters(make_config(), mcp_config)
    assert adapters["get_role_info"]()["role"] == "cop"
    assert adapters["health_check"]()["status"] == "ok"
    ok = adapters["get_observation"]([2, 2], [2, 3], TOKEN)
    assert ok["opponent_visible"] is True
    denied = adapters["get_observation"]([2, 2], [2, 3], "wrong")
    assert denied["error"] == "unauthorized"
    assert adapters["compose_message"]([2, 2], [2, 3], TOKEN)["message"]
    assert adapters["propose_action"]([2, 2], [2, 3], TOKEN)["action"]
    assert adapters["place_barrier_candidate"]([0, 0], [4, 4], [2, 2], TOKEN)["valid"] is True


def test_thief_adapters_callable_without_network(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    adapters = thief_tool_adapters(make_config(), mcp_config)
    assert adapters["get_role_info"]()["role"] == "thief"
    assert adapters["health_check"]()["status"] == "ok"
    assert adapters["get_observation"]([4, 4], [0, 0], TOKEN)["opponent_visible"] is False
    assert adapters["compose_message"]([4, 4], [0, 0], TOKEN)["message"]
    assert adapters["propose_action"]([4, 4], [0, 0], TOKEN)["action"]


def test_server_http_settings_reads_config(mcp_config):
    assert server_http_settings(mcp_config["cop_server"]) == ("127.0.0.1", 8001, "/mcp")
    assert server_http_settings(mcp_config["thief_server"]) == ("127.0.0.1", 8002, "/mcp")
