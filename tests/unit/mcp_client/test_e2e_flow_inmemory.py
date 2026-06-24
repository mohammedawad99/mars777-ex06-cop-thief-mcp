"""In-memory E2E flow tests (deterministic, no network) for coverage and logic.

Uses in-process FastMCP server objects as client targets, so the same flow code
runs without HTTP. The real HTTP path is covered by tests/integration/mcp.
"""

import asyncio
import json

from mars777_cop_thief.mcp_client.e2e_flow import run_flow
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server

COP_TOKEN = "dummy-cop"
THIEF_TOKEN = "dummy-thief"


def _servers(make_config, mcp_config):
    cfg = make_config()
    return build_cop_server(cfg, mcp_config), build_thief_server(cfg, mcp_config)


def test_flow_passes_against_in_memory_servers(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", COP_TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", THIEF_TOKEN)
    cop, thief = _servers(make_config, mcp_config)
    result = asyncio.run(run_flow(cop, thief, COP_TOKEN, THIEF_TOKEN))
    assert result["passed"] is True
    assert all(result["checks"].values())
    assert json.dumps(result)  # JSON-serializable smoke result


def test_flow_checks_individual_guarantees(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", COP_TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", THIEF_TOKEN)
    cop, thief = _servers(make_config, mcp_config)
    result = asyncio.run(run_flow(cop, thief, COP_TOKEN, THIEF_TOKEN))
    checks = result["checks"]
    assert checks["auth_negative"] is True
    assert checks["hidden_opponent_not_leaked"] is True
    assert checks["thief_no_barrier_tool"] is True
    assert checks["messages_plain_text"] is True
    assert checks["actions_structured"] is True
    assert result["thief"]["role"] == "thief"
    assert "place_barrier_candidate" not in result["thief"]["tools"]


def test_flow_fails_when_token_wrong(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", COP_TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", THIEF_TOKEN)
    cop, thief = _servers(make_config, mcp_config)
    # Wrong tokens → observation/message/action calls are rejected → flow fails.
    result = asyncio.run(run_flow(cop, thief, "incorrect", "incorrect"))
    assert result["passed"] is False
