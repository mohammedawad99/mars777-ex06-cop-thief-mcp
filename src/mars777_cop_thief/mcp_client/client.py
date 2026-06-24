"""Thin async helpers over the FastMCP ``Client`` for the local MCP servers.

These wrap the official FastMCP client; no transport details are reinvented. A
"target" is anything FastMCP accepts — an HTTP URL string for the real E2E path,
or an in-process ``FastMCP`` object for fast deterministic tests.
"""

from __future__ import annotations

import asyncio

from fastmcp import Client


def server_url(host: str, port: int, path: str) -> str:
    """Build the local HTTP MCP URL for a role server."""
    return f"http://{host}:{port}{path}"


def role_urls(mcp_config: dict, cop_port: int | None = None, thief_port: int | None = None) -> dict:
    """Return ``{"cop": url, "thief": url}`` from config, with optional ports."""
    cop, thief = mcp_config["cop_server"], mcp_config["thief_server"]
    return {
        "cop": server_url(cop["host"], cop_port or cop["port"], cop["path"]),
        "thief": server_url(thief["host"], thief_port or thief["port"], thief["path"]),
    }


async def wait_ready(target, attempts: int = 80, delay: float = 0.25) -> bool:
    """Poll a server with bounded retries until it answers a ping."""
    for _ in range(attempts):
        try:
            async with Client(target) as client:
                await client.ping()
                return True
        except Exception:
            await asyncio.sleep(delay)
    return False
