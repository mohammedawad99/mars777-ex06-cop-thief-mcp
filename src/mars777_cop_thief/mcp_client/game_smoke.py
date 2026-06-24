"""Local MCP-backed game smoke: real HTTP sub-games through both role servers.

Run with:

    uv run python -m mars777_cop_thief.mcp_client.game_smoke

Starts the Cop and Thief servers as local subprocesses (dummy in-process tokens,
never committed), plays the full default game over HTTP, prints a JSON summary,
and exits 0 only if every check passes. Always tears the servers down.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.mcp_client.client import wait_ready
from mars777_cop_thief.mcp_client.game_flow import run_mcp_full_game
from mars777_cop_thief.mcp_client.game_report import build_mcp_report
from mars777_cop_thief.mcp_client.subprocess_pair import server_pair
from mars777_cop_thief.shared.config import load_game_config

COP_TOKEN = "dummy-local-cop-token"
THIEF_TOKEN = "dummy-local-thief-token"
_ROOT = Path(__file__).resolve().parents[3]
GAME_CONFIG_PATH = _ROOT / "config" / "game.default.json"


def _checks(report: dict, results, num_sub_games: int, thief_tools, denied) -> dict:
    return {
        "sub_games_count": len(results) == num_sub_games,
        "all_decided": all(r.winner in {"cop", "thief"} for r in results),
        "hidden_state_respected": report["hidden_state_respected"],
        "transcripts_present": all(bool(r.transcript) for r in results),
        "actions_recorded": all(bool(r.events) for r in results),
        "thief_no_barrier_tool": "place_barrier_candidate" not in thief_tools,
        "auth_negative": denied.get("error") == "unauthorized",
    }


async def _play(game_config: dict, cop_url: str, thief_url: str, num_sub_games: int) -> dict:
    if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
        return {"passed": False, "error": "servers_not_ready"}
    engine = GameEngine(game_config)
    async with Client(cop_url) as cop, Client(thief_url) as thief:
        results = await run_mcp_full_game(engine, num_sub_games, cop, thief, COP_TOKEN, THIEF_TOKEN)
        thief_tools = sorted(tool.name for tool in await thief.list_tools())
        denied = (
            await cop.call_tool(
                "get_observation", {"cop": [0, 0], "thief": [1, 1], "auth_token": "wrong-token"}
            )
        ).data
    report = build_mcp_report(game_config, results, cop_url, thief_url)
    report["checks"] = _checks(report, results, num_sub_games, thief_tools, denied)
    report["passed"] = all(report["checks"].values())
    return report


def run_game_smoke(num_sub_games: int | None = None) -> dict:
    """Start both servers, play the MCP-backed game over HTTP, tear down."""
    game_config = load_game_config(GAME_CONFIG_PATH)
    count = num_sub_games or game_config["num_sub_games"]
    with server_pair(COP_TOKEN, THIEF_TOKEN) as urls:
        return asyncio.run(_play(game_config, urls["cop_url"], urls["thief_url"], count))


def main() -> int:
    report = run_game_smoke()
    print(json.dumps(report, indent=2))
    return 0 if report.get("passed") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
