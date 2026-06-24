"""Local Thief MCP server (HTTP).

Registers role-safe tools that delegate to the pure domain adapters. The thief
server deliberately **does not** expose barrier placement — that is a cop-only
capability. No LLM and no game rules live here.
"""

from __future__ import annotations

from fastmcp import FastMCP

from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.mcp_servers import tools
from mars777_cop_thief.shared.version import __version__

_ROLE = PlayerRole.THIEF


def thief_token_env(mcp_config: dict) -> str:
    """Return the env-var name holding the thief server token."""
    return mcp_config["thief_server"]["token_env_var"]


def thief_tool_adapters(game_config: dict, mcp_config: dict) -> dict:
    """Build the thief tool callables bound to config (no network)."""
    token_env = thief_token_env(mcp_config)

    def get_role_info() -> dict:
        return tools.role_info(_ROLE)

    def health_check() -> dict:
        return tools.health(_ROLE)

    def get_observation(
        cop: list[int],
        thief: list[int],
        auth_token: str,
        move_count: int = 0,
        barriers_placed: int = 0,
    ) -> dict:
        return tools.observation(
            game_config, _ROLE, cop, thief, token_env, auth_token, move_count, barriers_placed
        )

    def compose_message(
        cop: list[int],
        thief: list[int],
        auth_token: str,
        move_count: int = 0,
        barriers_placed: int = 0,
    ) -> dict:
        return tools.message(
            game_config, _ROLE, cop, thief, token_env, auth_token, move_count, barriers_placed
        )

    def propose_action(
        cop: list[int],
        thief: list[int],
        auth_token: str,
        move_count: int = 0,
        barriers_placed: int = 0,
    ) -> dict:
        return tools.proposed_action(
            game_config, _ROLE, cop, thief, token_env, auth_token, move_count, barriers_placed
        )

    return {
        "get_role_info": get_role_info,
        "health_check": health_check,
        "get_observation": get_observation,
        "compose_message": compose_message,
        "propose_action": propose_action,
    }


def build_thief_server(game_config: dict, mcp_config: dict) -> FastMCP:
    """Construct (but do not start) the Thief MCP server with its tools."""
    server = FastMCP(
        name="mars777-thief",
        version=__version__,
        instructions="Local Thief MCP server: role-safe observations and proposed actions.",
    )
    for name, fn in thief_tool_adapters(game_config, mcp_config).items():
        server.tool(fn, name=name)
    return server
