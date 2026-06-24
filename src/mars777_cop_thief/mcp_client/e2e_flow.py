"""Deterministic local MCP E2E flow over FastMCP client connections.

Calls each role server's tools and returns a JSON-serializable smoke result.
Works against either real HTTP URLs or in-process server objects (same code
path), so the flow logic is testable without a network.
"""

from __future__ import annotations

from fastmcp import Client

_COP = [0, 0]
_THIEF = [4, 4]  # Chebyshev distance 4 → opponent hidden at radius 1.


async def _role_checks(client: Client, token: str) -> dict:
    role = (await client.call_tool("get_role_info", {})).data
    health = (await client.call_tool("health_check", {})).data
    tools = sorted(tool.name for tool in await client.list_tools())
    args = {"cop": _COP, "thief": _THIEF}
    denied = (await client.call_tool("get_observation", {**args, "auth_token": "wrong-token"})).data
    observation = (await client.call_tool("get_observation", {**args, "auth_token": token})).data
    message = (await client.call_tool("compose_message", {**args, "auth_token": token})).data
    action = (await client.call_tool("propose_action", {**args, "auth_token": token})).data
    opponent_hidden = (
        observation.get("opponent_visible") is False
        and observation.get("opponent_position") is None
    )
    return {
        "role": role["role"],
        "health_ok": health["status"] == "ok",
        "tools": tools,
        "unauthorized_rejected": denied.get("error") == "unauthorized",
        "opponent_hidden": opponent_hidden,
        "message": message.get("message"),
        "message_is_text": isinstance(message.get("message"), str),
        "action_type": (action.get("action") or {}).get("type"),
    }


async def run_flow(cop_target, thief_target, cop_token: str, thief_token: str) -> dict:
    """Run the full deterministic E2E flow against both role servers."""
    async with Client(cop_target) as cop, Client(thief_target) as thief:
        c = await _role_checks(cop, cop_token)
        t = await _role_checks(thief, thief_token)
    cop_result, thief_result = c, t
    checks = {
        "cop_health": c["health_ok"],
        "thief_health": t["health_ok"],
        "cop_role_info": c["role"] == "cop",
        "thief_role_info": t["role"] == "thief",
        "auth_negative": c["unauthorized_rejected"] and t["unauthorized_rejected"],
        "hidden_opponent_not_leaked": c["opponent_hidden"] and t["opponent_hidden"],
        "messages_plain_text": c["message_is_text"] and t["message_is_text"],
        "actions_structured": c["action_type"] == "move" and t["action_type"] == "move",
        "thief_no_barrier_tool": "place_barrier_candidate" not in t["tools"],
    }
    return {
        "stage": "local-mcp-e2e",
        "transport": "http",
        "passed": all(checks.values()),
        "checks": checks,
        "cop": cop_result,
        "thief": thief_result,
    }
