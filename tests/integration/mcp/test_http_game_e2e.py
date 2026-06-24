"""Real HTTP MCP-backed game smoke: one sub-game driven over HTTP.

Starts the Cop and Thief servers as subprocesses and plays a single sub-game
through them over HTTP. Kept to one sub-game so the default suite stays fast; the
full 6-sub-game game is exercised by the `game_smoke` CLI command. Runs by
default; set ``RUN_MCP_E2E=0`` to skip where local subprocesses are not allowed.
"""

import os

import pytest

from mars777_cop_thief.mcp_client.game_smoke import run_game_smoke

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MCP_E2E") == "0",
    reason="MCP HTTP E2E disabled via RUN_MCP_E2E=0",
)


def test_http_mcp_game_runs_one_sub_game():
    report = run_game_smoke(num_sub_games=1)
    assert report["passed"] is True, report
    assert report["transport"] == "local_mcp_http"
    assert report["mcp_status"] == "local_verified"
    assert report["cloud_status"] == "not_deployed"
    assert report["email_status"] == "not_sent"
    assert len(report["sub_games"]) == 1
    checks = report["checks"]
    assert checks["all_decided"]
    assert checks["hidden_state_respected"]
    assert checks["transcripts_present"] and checks["actions_recorded"]
    assert checks["thief_no_barrier_tool"]
    assert checks["auth_negative"]
