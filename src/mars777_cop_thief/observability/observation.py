"""Per-agent partial observation under a visibility radius.

An Observation carries only what the agent is permitted to know. When the
opponent is outside the visibility radius its position is ``None`` — the hidden
coordinate is never stored on the observation, so it cannot leak to the agent.
"""

from __future__ import annotations

from dataclasses import dataclass

from mars777_cop_thief.game.models import PlayerRole, Position
from mars777_cop_thief.game.state import SubGameState
from mars777_cop_thief.observability.visibility import chebyshev, is_visible


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


@dataclass(frozen=True)
class Observation:
    """What one agent is allowed to know this turn."""

    role: PlayerRole
    self_position: Position
    rows: int
    cols: int
    move_count: int
    max_moves: int
    opponent_visible: bool
    opponent_position: Position | None
    visible_barriers: tuple[Position, ...]
    barrier_budget: int | None

    def to_dict(self) -> dict:
        """Fully JSON-serializable view (hidden opponent stays ``None``)."""
        opponent = self.opponent_position
        return {
            "role": self.role.value,
            "self_position": {"row": self.self_position.row, "col": self.self_position.col},
            "board": {"rows": self.rows, "cols": self.cols},
            "move_count": self.move_count,
            "max_moves": self.max_moves,
            "opponent_visible": self.opponent_visible,
            "opponent_position": (
                {"row": opponent.row, "col": opponent.col} if opponent is not None else None
            ),
            "visible_barriers": [{"row": b.row, "col": b.col} for b in self.visible_barriers],
            "barrier_budget": self.barrier_budget,
        }


def observe(state: SubGameState, role: PlayerRole, radius: int) -> Observation:
    """Build ``role``'s partial observation of ``state`` at the given radius."""
    me = state.position_of(role)
    opponent = state.position_of(_opponent(role))
    visible = is_visible(me, opponent, radius)
    barriers = tuple(
        b
        for b in sorted(state.barriers, key=lambda p: (p.row, p.col))
        if chebyshev(me, b) <= radius
    )
    budget = state.max_barriers - state.barriers_placed if role is PlayerRole.COP else None
    return Observation(
        role=role,
        self_position=me,
        rows=state.rows,
        cols=state.cols,
        move_count=state.move_count,
        max_moves=state.max_moves,
        opponent_visible=visible,
        opponent_position=opponent if visible else None,
        visible_barriers=barriers,
        barrier_budget=budget,
    )
