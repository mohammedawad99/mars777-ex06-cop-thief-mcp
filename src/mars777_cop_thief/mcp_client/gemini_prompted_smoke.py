"""Live-gated real-Gemini prompted MCP smoke.

Run with:

    uv run python -m mars777_cop_thief.mcp_client.gemini_prompted_smoke

By default (``RUN_GEMINI_LIVE`` not ``"1"``) it prints a skipped result and exits
0 — no network, no key required. When enabled with an API key set in the
environment it plays one short Gemini-driven sub-game over local HTTP and reports
provider/model/parse/token/cost (never the key), then tears the servers down.
"""

from __future__ import annotations

import asyncio
import json
import os

from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.llm.agent import LlmAgent
from mars777_cop_thief.llm.config import LlmConfigError, load_llm_config
from mars777_cop_thief.llm.provider_factory import build_gemini_provider
from mars777_cop_thief.mcp_client.client import wait_ready
from mars777_cop_thief.mcp_client.prompted_game_flow import new_accumulator, run_prompted_sub_game
from mars777_cop_thief.mcp_client.subprocess_pair import server_pair

COP_TOKEN = "dummy-local-cop-token"
THIEF_TOKEN = "dummy-local-thief-token"
# Tiny bounded board to keep a real Gemini smoke cheap (few API calls).
LIVE_CONFIG = {
    "group_code": "MaRs-777",
    "group_slug": "mars777",
    "github_repo": "REPLACE_WITH_GITHUB_REPO_URL",
    "grid_size": [3, 3],
    "max_moves": 4,
    "num_sub_games": 1,
    "max_barriers": 5,
    "allow_stay": False,
    "turn_order": ["thief", "cop"],
    "visibility_radius": 1,
    "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    "timezone": "Asia/Jerusalem",
}


def _summary(provider, results, acc) -> dict:
    result = results[0]
    return {
        "status": "ran",
        "passed": True,
        "llm_mode": "gemini",
        "provider_name": provider.provider_name,
        "model_name": provider.model_name,
        "winner": result.winner,
        "move_count": result.move_count,
        "parse_failures": acc["parse_failures"],
        "fallbacks_used": acc["fallbacks_used"],
        "total_prompt_tokens_estimate": acc["prompt_tokens"],
        "total_response_tokens_estimate": acc["response_tokens"],
        "estimated_cost_usd": round(acc["cost"], 6),
    }


async def _run_live(provider, cop_url, thief_url) -> dict:  # pragma: no cover - needs a real key
    if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
        return {"status": "error", "passed": False, "reason": "servers_not_ready"}
    engine = GameEngine(LIVE_CONFIG)
    agent = LlmAgent(provider)
    acc = new_accumulator()
    async with Client(cop_url) as cop, Client(thief_url) as thief:
        result = await run_prompted_sub_game(engine, cop, thief, agent, COP_TOKEN, THIEF_TOKEN, acc)
    return _summary(provider, [result], acc)


def run_gemini_smoke(env=None) -> dict:
    """Skip cleanly unless enabled; otherwise run one short live Gemini sub-game."""
    env = env if env is not None else os.environ
    config = load_llm_config()
    if env.get(config["live_smoke_enabled_env_var"]) != "1":
        return {"status": "skipped", "passed": True, "reason": "RUN_GEMINI_LIVE not set to 1"}
    try:
        provider = build_gemini_provider(config, env)
    except LlmConfigError as exc:
        return {"status": "error", "passed": False, "reason": str(exc)}
    with server_pair(COP_TOKEN, THIEF_TOKEN) as urls:  # pragma: no cover - needs a real key
        return asyncio.run(_run_live(provider, urls["cop_url"], urls["thief_url"]))


def main() -> int:
    result = run_gemini_smoke()
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
