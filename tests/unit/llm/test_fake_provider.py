"""Unit tests for the deterministic fake_local provider."""

from mars777_cop_thief.llm.fake_provider import FakeLocalProvider


def _complete(role, obs):
    return FakeLocalProvider().complete("prompt text", role=role, context={"observation": obs})


def test_response_is_deterministic_and_has_action(visible_obs):
    first = _complete("cop", visible_obs)
    second = _complete("cop", visible_obs)
    assert first.text == second.text
    assert "ACTION:" in first.text
    assert first.provider_name == "fake_local"
    assert first.metadata["llm_mode"] == "fake_local"


def test_hidden_response_has_no_coordinates(hidden_obs):
    text = _complete("cop", hidden_obs).text
    assert "cannot see" in text
    assert not any(ch.isdigit() for ch in text)  # never emits coordinates


def test_visible_response_uses_qualitative_direction(visible_obs):
    text = _complete("cop", visible_obs).text
    assert "visible to the" in text
    assert not any(ch.isdigit() for ch in text)


def test_supports_thief_role(hidden_obs):
    thief_obs = dict(hidden_obs, role="thief", self_position={"row": 4, "col": 4})
    text = _complete("thief", thief_obs).text
    assert "cop" in text
    assert "ACTION: move" in text


def test_stuck_actor_proposes_stay(hidden_obs):
    stuck = dict(hidden_obs, board={"rows": 1, "cols": 1}, self_position={"row": 0, "col": 0})
    text = _complete("cop", stuck).text
    assert "no legal move" in text
    assert "ACTION: stay" in text  # parser rejects this → orchestrator falls back


def test_token_estimates_present(visible_obs):
    response = _complete("cop", visible_obs)
    assert response.prompt_tokens_estimate > 0
    assert response.response_tokens_estimate > 0
    assert response.estimated_cost_usd == 0.0  # fake_local has no real spend
