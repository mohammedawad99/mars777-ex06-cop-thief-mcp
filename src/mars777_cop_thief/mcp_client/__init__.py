"""Local MCP client/orchestrator: HTTP client helpers and E2E smoke flow.

The client owns the trusted game state and calls the role servers' tools over
HTTP. Local-only — no public URLs, no cloud, no external LLM.
"""

from mars777_cop_thief.mcp_client.client import role_urls, server_url, wait_ready
from mars777_cop_thief.mcp_client.e2e_flow import run_flow
from mars777_cop_thief.mcp_client.subprocess_pair import server_pair

__all__ = [
    "role_urls",
    "run_flow",
    "server_pair",
    "server_url",
    "wait_ready",
]
