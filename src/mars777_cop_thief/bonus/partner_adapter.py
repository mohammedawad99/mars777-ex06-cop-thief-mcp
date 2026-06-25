"""Adapter for the partner group's MCP contract (setup / observe / my_move / state).

Pure translation/validation — **no network**. Our engine is already 0-based
``[row, col]`` (``game.models.Position``), matching the partner's canonical format,
so the adapter is mostly validation + payload shaping. Board size is configurable
(5x5 or 8x8); the official size is **not** frozen here. Tokens pass through
opaquely and are never logged.

CONFIRMED against partner group 'orcai-mj' live endpoints (Stage 15C). The earlier
provisional keys were wrong; the real contract is:

* token key is ``token`` (not ``auth_token``); a missing/invalid token is rejected.
* ``setup(cop, thief, rows, cols, origin, max_moves, max_barriers, diagonal, token)``
  — ``cop``/``thief`` are 0-based ``[row, col]`` **start positions** (required);
  ``origin`` is an integer (``0`` for 0-based indexing); ``diagonal`` is a bool.
  Returns ``{"role": "cop"|"thief", "snapshot": {...}}``.
* ``state(token)`` -> snapshot.
* ``my_move(token)`` -> ``{"message", "snapshot", "status"}`` — the partner's own
  agent makes *its* move; only valid on that role's turn (no move arg is sent).
* ``observe(message, mover, token)`` -> ``{"snapshot", "status"}`` — informs the
  partner that ``mover`` moved; the destination cell is parsed from ``message``.
* Thief moves first; snapshot ``turn`` starts at ``"thief"``.
"""

from __future__ import annotations

PARTNER_TOOLS = ("setup", "observe", "my_move", "state")
TOKEN_KEY = "token"
BOARD_SIZES = {"5x5": (5, 5), "8x8": (8, 8)}
DEFAULT_RULES = {
    "first_player": "thief",
    "num_sub_games": 6,
    "max_moves": 25,
    "max_barriers": 5,
    "movement": "diagonal",
    "coords": "0-based [row,col]",
    "origin": 0,
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


def default_starts(size_key: str) -> dict:
    """Canonical opposite-corner starts: cop top-left, thief bottom-right (0-based)."""
    rows, cols = board_dims(size_key)
    return {"cop": [0, 0], "thief": [rows - 1, cols - 1]}


def setup_args(
    size_key: str,
    *,
    token: str,
    cop_start=None,
    thief_start=None,
    origin: int = 0,
) -> dict:
    """Payload for the partner ``setup`` tool (board + start positions + rules + token)."""
    rows, cols = board_dims(size_key)
    starts = default_starts(size_key)
    cop = normalize_cell(cop_start if cop_start is not None else starts["cop"], size_key)
    thief = normalize_cell(thief_start if thief_start is not None else starts["thief"], size_key)
    return {
        "cop": cop,
        "thief": thief,
        "rows": rows,
        "cols": cols,
        "origin": origin,
        "max_moves": DEFAULT_RULES["max_moves"],
        "max_barriers": DEFAULT_RULES["max_barriers"],
        "diagonal": True,
        "token": token,
    }


def observe_message(cell, size_key: str, *, mover: str) -> str:
    """Build a ``move`` message the partner can parse a 0-based ``[row, col]`` from."""
    row, col = normalize_cell(cell, size_key)
    return f"{mover} moved to [{row}, {col}]"


def observe_args(message: str, mover: str, token: str) -> dict:
    """Payload for the partner ``observe`` tool (opponent move notification)."""
    return {"message": message, "mover": mover, "token": token}


def state_args(token: str) -> dict:
    return {"token": token}


def my_move_args(token: str) -> dict:
    """Payload for the partner ``my_move`` tool — the partner picks its own move."""
    return {"token": token}


def is_unauthorized(text) -> bool:
    """True when an error string/payload signals a rejected/missing token."""
    if isinstance(text, dict):
        text = text.get("error") or text.get("message") or ""
    low = str(text).lower()
    return "token" in low and ("invalid" in low or "missing" in low or "unauthorized" in low)


def warmup_plan(size_key: str, *, role: str, token: str) -> list:
    """Ordered ``(tool, args)`` calls for a valid one-exchange warm-up (no IO).

    Thief moves first, so the sequence differs by role: the thief server moves then
    hears the cop reply; the cop server hears the thief move then replies. Both touch
    all four tools in a legal turn order.
    """
    plan = [("setup", setup_args(size_key, token=token))]
    if role == "thief":
        plan += [
            ("my_move", my_move_args(token)),
            ("observe", observe_args(observe_message([1, 1], size_key, mover="cop"), "cop", token)),
            ("state", state_args(token)),
        ]
    else:  # cop
        thief_reply = [board_dims(size_key)[0] - 2, board_dims(size_key)[1] - 2]
        plan += [
            (
                "observe",
                observe_args(observe_message(thief_reply, size_key, mover="thief"), "thief", token),
            ),
            ("my_move", my_move_args(token)),
            ("state", state_args(token)),
        ]
    return plan
