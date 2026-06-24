"""Unit tests for the MCP client URL helpers."""

import asyncio

from mars777_cop_thief.mcp_client.client import role_urls, server_url, wait_ready


def test_server_url_builds_local_http_url():
    assert server_url("127.0.0.1", 8001, "/mcp") == "http://127.0.0.1:8001/mcp"


def test_role_urls_from_config(mcp_config):
    urls = role_urls(mcp_config)
    assert urls["cop"] == "http://127.0.0.1:8001/mcp"
    assert urls["thief"] == "http://127.0.0.1:8002/mcp"


def test_role_urls_accepts_port_overrides(mcp_config):
    urls = role_urls(mcp_config, cop_port=9101, thief_port=9102)
    assert urls["cop"].endswith(":9101/mcp")
    assert urls["thief"].endswith(":9102/mcp")


def test_wait_ready_returns_false_when_unreachable():
    # Nothing is listening on port 1; bounded to a single attempt → fast False.
    assert asyncio.run(wait_ready("http://127.0.0.1:1/mcp", attempts=1, delay=0.0)) is False
