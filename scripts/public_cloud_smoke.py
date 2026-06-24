"""Public Cloud Run MCP smoke (read-only; no token values printed).

Drives the two deployed MCP services over their public HTTPS URLs using the
existing deterministic E2E flow: each service must reject a bad token
(unauthorized) and accept the correct token (healthy / observation). URLs come
from COP_MCP_URL / THIEF_MCP_URL and tokens from COP_MCP_TOKEN / THIEF_MCP_TOKEN
in the environment. Token values are never printed and never written to the
sanitized result.

    COP_MCP_URL=... THIEF_MCP_URL=... \
    COP_MCP_TOKEN=... THIEF_MCP_TOKEN=... \
    uv run python scripts/public_cloud_smoke.py
"""

from __future__ import annotations

import asyncio
import json
import os

from mars777_cop_thief.mcp_client.client import wait_ready
from mars777_cop_thief.mcp_client.e2e_flow import run_flow


def _mcp_url(base: str) -> str:
    base = base.rstrip("/")
    return base if base.endswith("/mcp") else base + "/mcp"


async def _run(cop_url: str, thief_url: str, cop_token: str, thief_token: str) -> dict:
    if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
        return {"status": "unreachable", "passed": False}
    flow = await run_flow(cop_url, thief_url, cop_token, thief_token)
    checks = flow["checks"]
    summary = {
        "cop_unauthorized_rejected": flow["cop"]["unauthorized_rejected"],
        "thief_unauthorized_rejected": flow["thief"]["unauthorized_rejected"],
        "cop_authorized_health_ok": flow["cop"]["health_ok"],
        "thief_authorized_health_ok": flow["thief"]["health_ok"],
        "cop_role_info": checks["cop_role_info"],
        "thief_role_info": checks["thief_role_info"],
        "hidden_opponent_not_leaked": checks["hidden_opponent_not_leaked"],
        "thief_no_barrier_tool": checks["thief_no_barrier_tool"],
    }
    return {
        "status": "ok",
        "transport": "https",
        "passed": flow["passed"] and all(summary.values()),
        "checks": summary,
    }


def main() -> int:
    cop_url = _mcp_url(os.environ["COP_MCP_URL"])
    thief_url = _mcp_url(os.environ["THIEF_MCP_URL"])
    cop_token = os.environ["COP_MCP_TOKEN"]
    thief_token = os.environ["THIEF_MCP_TOKEN"]
    result = asyncio.run(_run(cop_url, thief_url, cop_token, thief_token))
    print(json.dumps(result, indent=2))  # contains no token values
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
