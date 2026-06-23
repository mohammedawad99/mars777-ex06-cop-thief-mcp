"""Plain event records describing applied actions.

Events are JSON-friendly dicts suitable for later transcript logging; this stage
only builds them, it does not write any files.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import (
    Action,
    PlayerRole,
    RuleViolation,
)


def _cell(pos: object) -> dict | None:
    """Serialise a Position-like object to a plain dict, or None."""
    if pos is None:
        return None
    return {"row": pos.row, "col": pos.col}


def build_event(
    action: Action,
    ok: bool,
    violation: RuleViolation | None,
    captured: bool,
    terminal: bool,
    winner: PlayerRole | None,
    move_count: int,
) -> dict:
    """Build a log-ready event dict for one attempted action."""
    return {
        "role": action.role.value,
        "action": action.type.value,
        "target": _cell(action.target),
        "direction": action.direction,
        "ok": ok,
        "violation": violation.value if violation is not None else None,
        "captured": captured,
        "terminal": terminal,
        "winner": winner.value if winner is not None else None,
        "move_count": move_count,
    }
