"""In-memory MCP-backed game flow tests (deterministic, no network).

Uses in-process FastMCP server objects as client targets so the same flow code
runs without HTTP. The real HTTP path is covered by tests/integration/mcp.
"""

import asyncio

import pytest
from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.mcp_client.game_flow import run_mcp_full_game, run_mcp_sub_game
from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server

TOKEN = "dummy"


def _servers(make_config, mcp_config, **overrides):
    cfg = make_config(**overrides)
    return cfg, build_cop_server(cfg, mcp_config), build_thief_server(cfg, mcp_config)


def _run_full(cfg, cop_srv, thief_srv, n):
    async def go():
        async with Client(cop_srv) as cop, Client(thief_srv) as thief:
            return await run_mcp_full_game(GameEngine(cfg), n, cop, thief, TOKEN, TOKEN)

    return asyncio.run(go())


def _run_sub(cfg, cop_srv, thief_srv, **kw):
    async def go():
        async with Client(cop_srv) as cop, Client(thief_srv) as thief:
            return await run_mcp_sub_game(GameEngine(cfg), cop, thief, TOKEN, TOKEN, **kw)

    return asyncio.run(go())


def test_full_game_runs_six_sub_games(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config)
    results = _run_full(cfg, cop, thief, 6)
    assert len(results) == 6
    for result in results:
        assert result.winner in {"cop", "thief"}
        assert result.transcript and result.events


def test_sub_game_records_messages_and_actions(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, max_moves=4)
    result = _run_sub(cfg, cop, thief)
    assert all({"sender", "message", "audit"} <= set(m) for m in result.transcript)
    assert all("ok" in e for e in result.events)
    assert not any(m["audit"]["leaked"] for m in result.transcript)  # no hidden leak


def test_sub_game_stops_on_capture(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    cfg, cop, thief = _servers(make_config, mcp_config, grid_size=[2, 2])
    result = _run_sub(cfg, cop, thief)
    assert result.winner == "cop"


def test_proposed_action_is_observation_based(make_config, mcp_config, monkeypatch):
    monkeypatch.setenv("COP_MCP_TOKEN", TOKEN)
    cop = build_cop_server(make_config(), mcp_config)

    async def call():
        async with Client(cop) as client:
            return (
                await client.call_tool(
                    "propose_action", {"cop": [0, 0], "thief": [0, 4], "auth_token": TOKEN}
                )
            ).data

    data = asyncio.run(call())
    # Thief at (0,4) is hidden at radius 1 → cop patrols toward centre (1,1),
    # NOT toward the hidden thief (which would be east → (0,1)). No cheating.
    assert data["action"]["target"] == {"row": 1, "col": 1}


class _R:
    def __init__(self, data):
        self.data = data


def _fake_client(action_payload):
    class _Fake:
        async def call_tool(self, name, args):
            if name == "get_observation":
                return _R({"opponent_visible": False, "opponent_position": None})
            if name == "compose_message":
                return _R({"message": "I cannot see the opponent right now."})
            return _R({"role": "x", "action": action_payload})

    return _Fake()


@pytest.mark.parametrize(
    "payload",
    [
        {"type": "move", "target": {"row": -1, "col": -1}},  # illegal → build + fallback
        None,  # not action_dict
        {"type": "move", "target": None},  # target is None
    ],
)
def test_bad_proposed_actions_fall_back(make_config, payload):
    engine = GameEngine(make_config(grid_size=[5, 5], max_moves=2))
    fake = _fake_client(payload)
    result = asyncio.run(run_mcp_sub_game(engine, fake, fake, TOKEN, TOKEN))
    assert result.winner in {"cop", "thief"}
    assert result.move_count >= 1


def test_stuck_actor_ends_sub_game(make_config):
    engine = GameEngine(make_config(grid_size=[1, 1]))
    fake = _fake_client(None)
    result = asyncio.run(run_mcp_sub_game(engine, fake, fake, TOKEN, TOKEN))
    assert result.winner == "thief"
    assert result.move_count == 0
