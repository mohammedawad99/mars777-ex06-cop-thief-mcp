"""Injected-client session wrappers used by the cross-group bonus referee.

``OurSession`` drives one of OUR stateless Cloud Run MCP role servers (our
existing ``compose_message``/``propose_action`` contract); ``PartnerSession``
drives a PARTNER stateful server (orcai-mj's confirmed ``setup``/``observe``/
``my_move`` contract). Both take an already-connected async client with a
``call_tool`` coroutine, so they are unit-testable with a fake client and never
embed transport details. Tokens pass through opaquely and are never logged.
"""

from __future__ import annotations

from mars777_cop_thief.bonus.partner_adapter import (
    my_move_args,
    observe_args,
    observe_message,
    setup_args,
)


class OurSession:
    """Drive one of our stateless MCP role servers; return a proposed target cell."""

    def __init__(self, client, token, role):
        self.client, self.token, self.role = client, token, role

    def _args(self, state) -> dict:
        return {
            "cop": [state.cop.row, state.cop.col],
            "thief": [state.thief.row, state.thief.col],
            "auth_token": self.token,
            "move_count": state.move_count,
            "barriers_placed": state.barriers_placed,
        }

    async def propose(self, state):
        """Return ``((row, col) | None, message)`` for the active role this turn."""
        args = self._args(state)
        message = (await self.client.call_tool("compose_message", args)).data.get("message")
        proposed = (await self.client.call_tool("propose_action", args)).data
        target = (proposed.get("action") or {}).get("target")
        pos = (target["row"], target["col"]) if target else None
        return pos, message


def _new_barrier(prev: dict, snap: dict):
    """First barrier cell present in ``snap`` but not ``prev`` (else None)."""
    old = {tuple(b) for b in (prev.get("barriers") or [])}
    for cell in snap.get("barriers") or []:
        if tuple(cell) not in old:
            return tuple(cell)
    return None


class PartnerSession:
    """Drive a partner MCP role server via the confirmed orcai-mj contract."""

    def __init__(self, client, token, role, size_key="8x8"):
        self.client, self.token, self.role, self.size = client, token, role, size_key
        self.snapshot: dict = {}

    async def setup(self, cop_start, thief_start):
        """Initialise the partner sub-game with the agreed starts; return its role."""
        args = setup_args(self.size, token=self.token, cop_start=cop_start, thief_start=thief_start)
        data = (await self.client.call_tool("setup", args)).data
        self.snapshot = data.get("snapshot") or {}
        return data.get("role")

    async def my_move(self):
        """Ask the partner agent for ITS own move; return ``(pos|None, barrier|None, message)``."""
        prev = self.snapshot
        data = (await self.client.call_tool("my_move", my_move_args(self.token))).data
        snap = data.get("snapshot") or {}
        barrier = _new_barrier(prev, snap)
        self.snapshot = snap
        pos = tuple(snap.get(self.role.value) or ())
        return (pos or None), barrier, data.get("message")

    async def observe(self, mover_role, cell):
        """Notify the partner that ``mover_role`` moved to ``cell`` (keeps it in sync)."""
        msg = observe_message(cell, self.size, mover=mover_role.value)
        data = (
            await self.client.call_tool("observe", observe_args(msg, mover_role.value, self.token))
        ).data
        self.snapshot = data.get("snapshot") or self.snapshot
