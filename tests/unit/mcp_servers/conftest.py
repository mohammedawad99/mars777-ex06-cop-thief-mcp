"""Fixtures for the local MCP server tests."""

import pytest


@pytest.fixture
def mcp_config() -> dict:
    return {
        "version": "1.00",
        "transport": "http",
        "local_only": True,
        "auth": {"enabled": True},
        "cop_server": {
            "host": "127.0.0.1",
            "port": 8001,
            "path": "/mcp",
            "token_env_var": "COP_MCP_TOKEN",
        },
        "thief_server": {
            "host": "127.0.0.1",
            "port": 8002,
            "path": "/mcp",
            "token_env_var": "THIEF_MCP_TOKEN",
        },
    }
