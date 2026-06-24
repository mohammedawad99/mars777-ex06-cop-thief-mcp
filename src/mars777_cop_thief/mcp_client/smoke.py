"""Local MCP E2E smoke: start both servers, run the flow over HTTP, print JSON.

Run with:

    uv run python -m mars777_cop_thief.mcp_client.smoke

Uses in-process dummy local tokens (not real secrets, never committed) injected
into the server subprocess environments. Exits 0 only if every check passes.
"""

from __future__ import annotations

import asyncio
import json

from mars777_cop_thief.mcp_client.client import wait_ready
from mars777_cop_thief.mcp_client.e2e_flow import run_flow
from mars777_cop_thief.mcp_client.subprocess_pair import server_pair

# Dummy local-only tokens generated in process memory (not real secrets).
COP_TOKEN = "dummy-local-cop-token"
THIEF_TOKEN = "dummy-local-thief-token"


async def _drive(cop_url: str, thief_url: str) -> dict:
    cop_ready = await wait_ready(cop_url)
    thief_ready = await wait_ready(thief_url)
    if not (cop_ready and thief_ready):
        return {"stage": "local-mcp-e2e", "passed": False, "error": "servers_not_ready"}
    return await run_flow(cop_url, thief_url, COP_TOKEN, THIEF_TOKEN)


def run_smoke() -> dict:
    """Start both servers, run the E2E flow over HTTP, and tear them down."""
    with server_pair(COP_TOKEN, THIEF_TOKEN) as urls:
        return asyncio.run(_drive(urls["cop_url"], urls["thief_url"]))


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
