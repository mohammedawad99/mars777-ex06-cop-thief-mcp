"""Shared helpers for the local MCP server adapters (domain delegation only).

These helpers translate plain JSON-friendly inputs into domain objects and back.
They hold no game rules of their own — the engine remains authoritative.
"""

from __future__ import annotations

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.game.models import Action, Position
from mars777_cop_thief.game.state import SubGameState

STAGE = "local-mcp"


def to_position(cell: list[int]) -> Position:
    """Convert a ``[row, col]`` pair into a Position."""
    return Position(int(cell[0]), int(cell[1]))


def build_state(
    game_config: dict,
    cop: list[int],
    thief: list[int],
    move_count: int = 0,
    barriers_placed: int = 0,
) -> SubGameState:
    """Build an ephemeral sub-game state from authoritative positions."""
    state = GameEngine(game_config).new_subgame(to_position(cop), to_position(thief))
    state.move_count = int(move_count)
    state.barriers_placed = int(barriers_placed)
    return state


def action_to_dict(action: Action | None) -> dict | None:
    """Serialise an Action into a JSON-friendly dict, or None."""
    if action is None:
        return None
    target = action.target
    return {
        "type": action.type.value,
        "target": {"row": target.row, "col": target.col} if target else None,
        "direction": action.direction,
    }


def server_http_settings(server_config: dict) -> tuple[str, int, str]:
    """Return ``(host, port, path)`` for one role's local server config."""
    return server_config["host"], int(server_config["port"]), server_config["path"]
