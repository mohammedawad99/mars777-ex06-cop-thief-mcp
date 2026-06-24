"""Natural-language transcript records (evidence/audit only).

The ``message`` is the only text the recipient may read. The ``audit`` block is
debug/evidence metadata and must never be consumed by the other agent as hidden
side-channel communication. Audit never carries the opponent's exact hidden
coordinates — only qualitative, already-disclosed facts.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.observability.observation import Observation
from mars777_cop_thief.observability.visibility import relative_direction


def audit_facts(obs: Observation) -> dict:
    """Debug-only interpreted facts about the sender's own observation."""
    direction = None
    if obs.opponent_visible and obs.opponent_position is not None:
        direction = relative_direction(obs.self_position, obs.opponent_position)
    return {
        "opponent_visible": obs.opponent_visible,
        "self_position": {"row": obs.self_position.row, "col": obs.self_position.col},
        "relative_direction": direction,
        "visible_barrier_count": len(obs.visible_barriers),
    }


def make_message_event(
    turn_index: int,
    sender: PlayerRole,
    recipient: PlayerRole,
    text: str,
    opponent_visible: bool,
    audit: dict,
) -> dict:
    """Build a transcript record for one natural-language message."""
    return {
        "turn_index": turn_index,
        "sender": sender.value,
        "recipient": recipient.value,
        "message": text,
        "opponent_visible": opponent_visible,
        "audit": audit,
    }
