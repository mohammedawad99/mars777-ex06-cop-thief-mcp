"""Import-safety of run entrypoints and validation of the local MCP config."""

import importlib
from pathlib import Path

from mars777_cop_thief.shared.config import load_json_config

MCP_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "mcp.local.default.json"


def test_run_modules_import_without_starting_servers():
    for name in ("run_cop", "run_thief"):
        module = importlib.import_module(f"mars777_cop_thief.mcp_servers.{name}")
        assert callable(module.main)


def test_local_mcp_config_has_expected_settings():
    config = load_json_config(MCP_CONFIG_PATH)
    assert config["transport"] in {"http", "streamable-http"}
    assert config["local_only"] is True
    assert config["auth"]["enabled"] is True
    assert config["cop_server"]["port"] == 8001
    assert config["thief_server"]["port"] == 8002
    assert config["cop_server"]["token_env_var"] == "COP_MCP_TOKEN"
    assert config["thief_server"]["token_env_var"] == "THIEF_MCP_TOKEN"
