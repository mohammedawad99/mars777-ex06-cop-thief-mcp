"""Unit tests for the role-specific prompt builder."""

from mars777_cop_thief.llm.prompts import build_prompt


def test_visible_opponent_described_qualitatively(visible_obs):
    prompt = build_prompt(visible_obs, None, "cop")
    assert "visible to the east" in prompt
    assert "col 3" not in prompt  # opponent's exact coordinate is never included


def test_hidden_opponent_not_described_with_coordinates(hidden_obs):
    prompt = build_prompt(hidden_obs, None, "cop")
    assert "not visible" in prompt
    assert "opponent_position" not in prompt
    assert "ACTION:" in prompt


def test_prompt_includes_role_board_and_allowed_actions(visible_obs):
    prompt = build_prompt(visible_obs, None, "cop")
    assert "You are the COP" in prompt
    assert "Board: 5x5" in prompt
    assert "move <direction>" in prompt
    assert "barrier <direction>" in prompt  # cop only


def test_thief_prompt_has_no_barrier_action(visible_obs):
    thief_obs = dict(visible_obs, role="thief")
    prompt = build_prompt(thief_obs, None, "thief")
    assert "barrier <direction>" not in prompt


def test_prompt_includes_last_message_when_present(visible_obs):
    prompt = build_prompt(visible_obs, "I cannot see you right now.", "cop")
    assert "Last message from the other agent" in prompt
    assert "I cannot see you right now." in prompt


def test_prompt_has_no_secrets(visible_obs):
    prompt = build_prompt(visible_obs, None, "cop").lower()
    assert "auth_token" not in prompt
    assert "token" not in prompt
