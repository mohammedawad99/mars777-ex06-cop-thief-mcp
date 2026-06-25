"""Unit tests for the bonus referee sessions with a fake MCP client (no network)."""

import asyncio

from mars777_cop_thief.bonus.cross_engine import bonus_engine
from mars777_cop_thief.bonus.sessions import OurSession, PartnerSession, _new_barrier
from mars777_cop_thief.game.models import PlayerRole, Position


class _Resp:
    def __init__(self, data):
        self.data = data


class FakeClient:
    """Minimal async MCP client: dispatches call_tool to per-tool handlers."""

    def __init__(self, handlers):
        self.handlers = handlers
        self.calls = []

    async def call_tool(self, name, args):
        self.calls.append((name, dict(args)))
        return _Resp(self.handlers[name](args))


def _state():
    return bonus_engine().new_subgame(Position(0, 0), Position(7, 7))


def test_our_session_proposes_target_and_passes_positions():
    client = FakeClient(
        {
            "compose_message": lambda a: {"message": "cop here"},
            "propose_action": lambda a: {"action": {"target": {"row": 1, "col": 1}}},
        }
    )
    pos, message = asyncio.run(OurSession(client, "tok", None).propose(_state()))
    assert pos == (1, 1) and message == "cop here"
    sent = client.calls[0][1]
    assert sent["cop"] == [0, 0] and sent["thief"] == [7, 7] and sent["auth_token"] == "tok"


def test_our_session_none_target_when_no_action():
    client = FakeClient(
        {"compose_message": lambda a: {}, "propose_action": lambda a: {"action": None}}
    )
    pos, message = asyncio.run(OurSession(client, "t", None).propose(_state()))
    assert pos is None and message is None


def test_new_barrier_detects_added_cell():
    assert _new_barrier({"barriers": [[1, 1]]}, {"barriers": [[1, 1], [3, 3]]}) == (3, 3)
    assert _new_barrier({"barriers": []}, {"barriers": []}) is None


def test_partner_session_setup_my_move_observe():
    client = FakeClient(
        {
            "setup": lambda a: {"role": "thief", "snapshot": {"thief": [7, 7], "barriers": []}},
            "my_move": lambda a: {"message": "slip", "snapshot": {"thief": [6, 6], "barriers": []}},
            "observe": lambda a: {"snapshot": {"thief": [6, 6], "barriers": []}},
        }
    )
    session = PartnerSession(client, "ptok", PlayerRole.THIEF)

    async def go():
        role = await session.setup([0, 0], [7, 7])
        mv = await session.my_move()
        await session.observe(PlayerRole.COP, [1, 1])
        return role, mv

    role, (pos, barrier, msg) = asyncio.run(go())
    assert role == "thief" and pos == (6, 6) and barrier is None and msg == "slip"
    setup_args = client.calls[0][1]
    assert setup_args["rows"] == 8 and setup_args["token"] == "ptok" and setup_args["cop"] == [0, 0]
    assert "cop moved to [1, 1]" in client.calls[-1][1]["message"]


def test_partner_session_my_move_reports_barrier():
    client = FakeClient(
        {
            "setup": lambda a: {"role": "cop", "snapshot": {"cop": [0, 0], "barriers": []}},
            "my_move": lambda a: {
                "message": "wall",
                "snapshot": {"cop": [0, 0], "barriers": [[3, 3]]},
            },
        }
    )
    session = PartnerSession(client, "t", PlayerRole.COP)

    async def go():
        await session.setup([0, 0], [7, 7])
        return await session.my_move()

    pos, barrier, msg = asyncio.run(go())
    assert pos == (0, 0) and barrier == (3, 3)
