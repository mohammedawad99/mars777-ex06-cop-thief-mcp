"""Local Cop MCP server entrypoint (HTTP).

Run locally with:

    uv run python -m mars777_cop_thief.mcp_servers.run_cop

Importing this module does not start a server; only ``main()`` does.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.mcp_servers.common import resolve_port, server_http_settings
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.shared.config import load_game_config, load_json_config

_ROOT = Path(__file__).resolve().parents[3]
GAME_CONFIG_PATH = _ROOT / "config" / "game.default.json"
MCP_CONFIG_PATH = _ROOT / "config" / "mcp.local.default.json"


def main() -> None:  # pragma: no cover - starts a long-running server
    game_config = load_game_config(GAME_CONFIG_PATH)
    mcp_config = load_json_config(MCP_CONFIG_PATH)
    server = build_cop_server(game_config, mcp_config)
    host, _, path = server_http_settings(mcp_config["cop_server"])
    port = resolve_port(mcp_config["cop_server"], "COP_MCP_PORT")
    server.run(transport=mcp_config["transport"], host=host, port=port, path=path)


if __name__ == "__main__":  # pragma: no cover
    main()
