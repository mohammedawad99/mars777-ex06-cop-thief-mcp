"""Real HTTP end-to-end smoke: two local MCP servers driven by the client.

This starts the Cop and Thief servers as subprocesses on free local ports,
connects over HTTP, and asserts every smoke check passes. It is deterministic and
fast (a few seconds) and runs by default. Set ``RUN_MCP_E2E=0`` to skip it in
environments that cannot spawn local subprocesses.
"""

import os

import pytest

from mars777_cop_thief.mcp_client.smoke import run_smoke

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MCP_E2E") == "0",
    reason="MCP HTTP E2E disabled via RUN_MCP_E2E=0",
)


def test_http_e2e_smoke_passes():
    result = run_smoke()
    assert result["passed"] is True, result
    checks = result["checks"]
    assert checks["cop_health"] and checks["thief_health"]
    assert checks["cop_role_info"] and checks["thief_role_info"]
    assert checks["auth_negative"]
    assert checks["hidden_opponent_not_leaked"]
    assert checks["messages_plain_text"]
    assert checks["actions_structured"]
    assert checks["thief_no_barrier_tool"]
    assert "place_barrier_candidate" not in result["thief"]["tools"]
