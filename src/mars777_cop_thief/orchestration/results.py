"""Structured, JSON-serializable records for local self-play.

These records back the in-memory report; they hold no behaviour and serialise
with the standard library ``json`` module. This is a structured transcript, not
the later natural-language transcript.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mars777_cop_thief.game.models import Action, ActionResult, PlayerRole, Position
from mars777_cop_thief.game.state import SubGameState


def cell(pos: Position) -> dict:
    """Serialise a Position to a plain ``{"row", "col"}`` dict."""
    return {"row": pos.row, "col": pos.col}


def snapshot(state: SubGameState) -> dict:
    """Both players' positions at a point in time."""
    return {"cop": cell(state.cop), "thief": cell(state.thief)}


def make_event(
    turn_index: int,
    actor: PlayerRole,
    action: Action | None,
    result: ActionResult | None,
    before: dict,
    after: dict,
) -> dict:
    """Build a log-ready event for one attempted turn."""
    return {
        "turn_index": turn_index,
        "actor": actor.value,
        "action": action.type.value if action is not None else None,
        "target": cell(action.target) if action is not None and action.target else None,
        "ok": bool(result is not None and result.ok),
        "violation": result.violation.value if result is not None and result.violation else None,
        "captured": bool(result is not None and result.captured),
        "winner": result.winner.value if result is not None and result.winner else None,
        "before": before,
        "after": after,
    }


@dataclass
class SubGameResult:
    """Outcome of one sub-game, with its full structured transcript."""

    index: int
    rows: int
    cols: int
    winner: str | None
    scores: dict
    cop_start: Position
    thief_start: Position
    cop_final: Position
    thief_final: Position
    move_count: int
    barriers: list[Position]
    events: list[dict]
    transcript: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a fully JSON-serializable view of this result."""
        return {
            "index": self.index,
            "board": {"rows": self.rows, "cols": self.cols},
            "winner": self.winner,
            "scores": self.scores,
            "start": {"cop": cell(self.cop_start), "thief": cell(self.thief_start)},
            "final": {"cop": cell(self.cop_final), "thief": cell(self.thief_final)},
            "move_count": self.move_count,
            "barriers": [cell(b) for b in self.barriers],
            "events": self.events,
            "transcript": self.transcript,
        }
