"""Unit tests for the action parser."""

from mars777_cop_thief.llm.parser import parse_action


def test_accepts_hyphenated_direction():
    result = parse_action("I will go. ACTION: move north-east", "cop")
    assert result.ok
    assert result.action_type == "move"
    assert result.direction == "northeast"


def test_accepts_plain_direction():
    result = parse_action("ACTION: move northeast", "thief")
    assert result.ok
    assert result.direction == "northeast"


def test_accepts_underscore_direction():
    assert parse_action("ACTION: move south_west", "thief").direction == "southwest"


def test_cop_can_place_barrier():
    result = parse_action("Block it. ACTION: barrier south", "cop")
    assert result.ok
    assert result.action_type == "barrier"
    assert result.direction == "south"


def test_thief_cannot_place_barrier():
    result = parse_action("ACTION: barrier south", "thief")
    assert not result.ok
    assert result.error == "thief_cannot_place_barrier"


def test_rejects_stay():
    assert parse_action("ACTION: stay", "cop").error == "stay_not_allowed"


def test_rejects_missing_action_line():
    assert parse_action("I will think about my move.", "cop").error == "no_action_line"


def test_rejects_unknown_action_and_direction():
    assert parse_action("ACTION: fly up", "cop").error == "unknown_action"
    assert parse_action("ACTION: move sideways", "cop").error == "unknown_direction"
    assert parse_action("ACTION: move", "cop").error == "missing_direction"


def test_uses_last_action_line():
    text = "ACTION: move north\nactually no. ACTION: move south"
    assert parse_action(text, "cop").direction == "south"


def test_rejects_empty_action_line():
    assert parse_action("ACTION:", "cop").error == "no_action_line"
    assert parse_action("ACTION:   ", "cop").error == "no_action_line"
