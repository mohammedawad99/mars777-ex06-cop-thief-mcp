"""Role-specific prompt builder for the LLM agents.

Prompts are built only from the role-safe observation. The opponent is described
with a qualitative relative direction when visible and never with exact
coordinates; when hidden it is reported as not visible. No tokens, env vars, or
secrets ever appear in a prompt.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import Position
from mars777_cop_thief.observability.visibility import relative_direction

_RULES = (
    "one step per turn in 8 directions (incl. diagonals); staying is not allowed. "
    "The cop catches the thief by moving onto its cell; the thief wins by surviving "
    "all moves. The cop may place up to 5 barriers; the thief may not."
)


def _opponent_word(role: str) -> str:
    return "thief" if role == "cop" else "cop"


def _visible_line(observation: dict, role: str) -> str:
    opponent = _opponent_word(role)
    if observation["opponent_visible"] and observation.get("opponent_position"):
        me = Position(observation["self_position"]["row"], observation["self_position"]["col"])
        opp = Position(
            observation["opponent_position"]["row"], observation["opponent_position"]["col"]
        )
        direction = relative_direction(me, opp) or "right next to you"
        return f"The {opponent} is visible to the {direction}."
    return f"The {opponent} is not visible right now."


def build_prompt(observation: dict, message, role: str) -> str:
    """Build a role-specific natural-language prompt from a role-safe observation."""
    me, board = observation["self_position"], observation["board"]
    lines = [
        f"You are the {role.upper()} in a Cop-and-Thief grid game.",
        f"Board: {board['rows']}x{board['cols']}. Move {observation['move_count']} "
        f"of {observation['max_moves']}.",
        f"Your position: row {me['row']}, col {me['col']}.",
        _visible_line(observation, role),
        f"Visible barriers near you: {len(observation.get('visible_barriers', []))}.",
    ]
    if role == "cop":
        lines.append(f"Your remaining barrier budget: {observation.get('barrier_budget')}.")
    if message:
        lines.append(f'Last message from the other agent: "{message}"')
    extra = "; or 'barrier <direction>'" if role == "cop" else ""
    lines.append(f"Allowed actions: 'move <direction>'{extra}.")
    lines.append(f"Rules: {_RULES}")
    lines.append(
        f"Explain your reasoning briefly, then end with a line 'ACTION: move <direction>'{extra}."
    )
    return "\n".join(lines)
