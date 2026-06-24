"""Real HTTP prompted MCP-backed game smoke: one sub-game over HTTP.

Starts both servers and plays a single prompted sub-game (fake_local provider)
over HTTP. Kept to one sub-game so the default suite stays fast; the full game is
exercised by the `prompted_game_smoke` CLI. Set ``RUN_MCP_E2E=0`` to skip.
"""

import os

import pytest

from mars777_cop_thief.mcp_client.prompted_game_smoke import run_prompted_game_smoke

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MCP_E2E") == "0",
    reason="MCP HTTP E2E disabled via RUN_MCP_E2E=0",
)


def test_prompted_http_game_runs_one_sub_game():
    report = run_prompted_game_smoke(num_sub_games=1)
    assert report["passed"] is True, report
    assert report["llm_mode"] == "fake_local"
    assert report["mode"] == "mcp-backed-prompted"
    assert report["provider_name"] == "fake_local"
    assert len(report["sub_games"]) == 1
    assert report["total_prompt_tokens_estimate"] > 0
    assert report["estimated_cost_usd"] >= 0
    checks = report["checks"]
    assert checks["hidden_state_respected"]
    assert checks["thief_no_barrier_tool"]
    assert checks["token_accounting"]
