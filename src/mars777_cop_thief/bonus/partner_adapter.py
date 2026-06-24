"""Adapter for the partner group's MCP contract (setup / observe / my_move / state).

Pure translation/validation — **no network**. Our engine is already 0-based
``[row, col]`` (``game.models.Position``), matching the partner's canonical format,
so the adapter is mostly validation + payload shaping. Board size is configurable
(5x5 or 8x8); the official size is **not** frozen here. Tokens pass through
opaquely and are never logged.

NOTE: the partner's exact tool argument keys could not be read from their (currently
non-public) INTEROP doc. The payload keys below follow the agreed contract (thief-
first, 0-based ``[row, col]``, diagonal movement, ≤25 moves, ≤5 cop barriers) and the
common MCP ``auth_token`` convention; they must be confirmed against the live partner
endpoints before the official run.
"""

from __future__ import annotations

PARTNER_TOOLS = ("setup", "observe", "my_move", "state")
BOARD_SIZES = {"5x5": (5, 5), "8x8": (8, 8)}
DEFAULT_RULES = {
    "first_player": "thief",
    "num_sub_games": 6,
    "max_moves": 25,
    "max_barriers": 5,
    "movement": "diagonal",
    "coords": "0-based [row,col]",
}


class AdapterError(ValueError):
    """Invalid coordinate, board size, or partner tool set."""


def board_dims(size_key: str) -> tuple[int, int]:
    """Return ``(rows, cols)`` for a supported board size key."""
    if size_key not in BOARD_SIZES:
        raise AdapterError(f"unsupported board size '{size_key}'; use {list(BOARD_SIZES)}")
    return BOARD_SIZES[size_key]


def normalize_cell(cell, size_key: str) -> list[int]:
    """Validate a 0-based ``[row, col]`` cell against the board; return ``[row, col]``."""
    if not (isinstance(cell, (list, tuple)) and len(cell) == 2):
        raise AdapterError("cell must be a [row, col] pair")
    row, col = int(cell[0]), int(cell[1])
    rows, cols = board_dims(size_key)
    if not (0 <= row < rows and 0 <= col < cols):
        raise AdapterError(f"cell {[row, col]} out of bounds for {size_key}")
    return [row, col]


def supported_contract(tool_names) -> bool:
    """True only when the partner exposes all four required tools."""
    return set(PARTNER_TOOLS).issubset(set(tool_names))


def setup_args(size_key: str, *, role: str, token: str) -> dict:
    """Payload for the partner ``setup`` tool (board/role/rules + token)."""
    rows, cols = board_dims(size_key)
    return {
        "auth_token": token,
        "role": role,
        "board": [rows, cols],
        "first_player": DEFAULT_RULES["first_player"],
        "max_moves": DEFAULT_RULES["max_moves"],
        "max_barriers": DEFAULT_RULES["max_barriers"],
        "coords": DEFAULT_RULES["coords"],
    }


def observe_args(token: str) -> dict:
    return {"auth_token": token}


def state_args(token: str) -> dict:
    return {"auth_token": token}


def my_move_args(cell, size_key: str, *, token: str) -> dict:
    """Payload for the partner ``my_move`` tool with a validated 0-based cell."""
    return {"auth_token": token, "move": normalize_cell(cell, size_key)}


def warmup_plan(size_key: str, *, role: str, token: str) -> list:
    """Ordered ``(tool, args)`` calls for a warm-up sub-game on a board (no IO)."""
    rows, cols = board_dims(size_key)
    sample = [1 if rows > 1 else 0, 1 if cols > 1 else 0]
    return [
        ("setup", setup_args(size_key, role=role, token=token)),
        ("observe", observe_args(token)),
        ("my_move", my_move_args(sample, size_key, token=token)),
        ("state", state_args(token)),
    ]
