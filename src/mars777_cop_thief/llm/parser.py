"""Parse a game action from a free-text LLM-like response.

The action is taken from the last ``ACTION:`` line. Move directions accept
hyphen/underscore variants ("north-east", "north_east", "northeast"). Stay/no-op
and malformed actions are rejected with a structured error; barrier placement is
cop-only.
"""

from __future__ import annotations

from dataclasses import dataclass

_CANONICAL = (
    "north",
    "south",
    "east",
    "west",
    "northeast",
    "northwest",
    "southeast",
    "southwest",
)
_STAY = ("stay", "wait", "hold", "noop", "none", "pass")


@dataclass(frozen=True)
class ParsedAction:
    """Outcome of parsing one action line."""

    ok: bool
    action_type: str | None = None
    direction: str | None = None
    error: str | None = None


def _normalize(token: str) -> str:
    return token.lower().replace("-", "").replace("_", "")


def _action_line(text: str) -> str | None:
    for line in reversed(text.splitlines()):
        lowered = line.lower()
        if "action:" in lowered:
            return line[lowered.index("action:") + len("action:") :].strip()
    return None


def _parse_directioned(tokens: list[str], action_type: str) -> ParsedAction:
    if len(tokens) < 2:
        return ParsedAction(False, error="missing_direction")
    direction = _normalize(tokens[1])
    if direction not in _CANONICAL:
        return ParsedAction(False, error="unknown_direction")
    return ParsedAction(True, action_type, direction)


def parse_action(text: str, role: str) -> ParsedAction:
    """Parse the action from ``text`` for ``role`` ('cop' or 'thief')."""
    line = _action_line(text)
    if not line:
        return ParsedAction(False, error="no_action_line")
    tokens = line.split()
    verb = _normalize(tokens[0])
    if verb in _STAY:
        return ParsedAction(False, error="stay_not_allowed")
    if verb == "move":
        return _parse_directioned(tokens, "move")
    if verb == "barrier":
        if role != "cop":
            return ParsedAction(False, error="thief_cannot_place_barrier")
        return _parse_directioned(tokens, "barrier")
    return ParsedAction(False, error="unknown_action")
