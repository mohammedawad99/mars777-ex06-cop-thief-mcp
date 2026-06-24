"""Free natural-language message generation from an Observation.

Messages are plain English strings — never JSON, never a numeric protocol, and
never the opponent's exact coordinates. A hidden opponent yields a "cannot see"
message; a visible opponent is described with a qualitative relative direction.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.observability.observation import Observation
from mars777_cop_thief.observability.visibility import relative_direction


def compose_message(obs: Observation) -> str:
    """Return a free natural-language line describing what the agent senses."""
    if obs.opponent_visible and obs.opponent_position is not None:
        direction = relative_direction(obs.self_position, obs.opponent_position)
        if direction is None:
            return "I can see movement nearby; the opponent is right on top of me."
        return f"I can see movement nearby; the opponent seems close to the {direction}."
    if obs.role is PlayerRole.COP:
        return "I cannot see the thief right now; I am guarding nearby corridors."
    return "I cannot see the cop right now; I am staying cautious and exploring."
