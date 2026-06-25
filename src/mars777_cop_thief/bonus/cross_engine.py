"""Official inter-group bonus rules: an 8x8, thief-first canonical GameEngine.

Encodes the rules confirmed in writing with partner group 'orcai-mj' (8x8 board,
0-based ``[row, col]``, thief-first, 6 sub-games, <=25 moves, <=5 cop-only
barriers, diagonal movement) and builds a ``GameEngine`` that scores per the
agreed bonus scheme (Cop win: cop 20 / thief 5; Thief win: thief 10 / cop 5).
The engine is the single canonical authority for legality/capture/scoring.
"""

from __future__ import annotations

from mars777_cop_thief.game.engine import GameEngine

OFFICIAL_RULES = {
    "board_size": [8, 8],
    "origin": 0,
    "coordinate_format": "[row, col]",
    "turn_order": ["thief", "cop"],
    "num_sub_games": 6,
    "max_moves": 25,
    "max_barriers": 5,
    "barriers_role": "cop",
    "diagonal_movement": True,
    "scoring": {
        "cop_win": {"cop": 20, "thief": 5},
        "thief_win": {"cop": 5, "thief": 10},
    },
    "max_moves_note": "25 plies total (thief-first); thief survival to the limit is a thief win.",
}

DEFAULT_COP_START = [0, 0]
DEFAULT_THIEF_START = [7, 7]


def bonus_engine() -> GameEngine:
    """Return a ``GameEngine`` configured for the agreed official bonus rules."""
    return GameEngine(
        {
            "grid_size": OFFICIAL_RULES["board_size"],
            "max_moves": OFFICIAL_RULES["max_moves"],
            "max_barriers": OFFICIAL_RULES["max_barriers"],
            "allow_stay": False,
            "turn_order": OFFICIAL_RULES["turn_order"],
            "scoring": {"cop_win": 20, "thief_loss": 5, "cop_loss": 5, "thief_win": 10},
        }
    )


def outcome_reason(winner: str | None, move_count: int, max_moves: int) -> str:
    """Human-readable reason a sub-game ended."""
    if winner == "cop":
        return "capture"
    if winner == "thief":
        return "thief_survived_max_moves" if move_count >= max_moves else "thief_survived"
    return "undecided"
