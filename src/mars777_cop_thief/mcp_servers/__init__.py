"""Local HTTP MCP servers for the Cop and Thief roles.

The servers expose role-safe tools that delegate to the domain packages; the LLM
lives in the future client, not here. This stage is local-only — no public URLs
and no cloud deployment.
"""

from mars777_cop_thief.mcp_servers.auth import check_auth
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server, cop_tool_adapters
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server, thief_tool_adapters

__all__ = [
    "build_cop_server",
    "build_thief_server",
    "check_auth",
    "cop_tool_adapters",
    "thief_tool_adapters",
]
