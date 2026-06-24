"""Unit tests for the LLM agent (provider + prompt + parser)."""

from mars777_cop_thief.llm.agent import LlmAgent
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.provider import LlmResponse


class _StubProvider:
    provider_name = "stub"
    model_name = "stub-v0"

    def __init__(self, text):
        self._text = text

    def complete(self, prompt, *, role, context):
        return LlmResponse(self._text, self.provider_name, self.model_name, 5, 3, 0.0, {})


def test_agent_returns_structured_decision(visible_obs):
    decision = LlmAgent(FakeLocalProvider()).decide(visible_obs, None, "cop")
    assert decision.parsed_ok is True
    assert decision.action_type == "move"
    assert decision.direction
    assert decision.prompt_tokens_estimate > 0
    assert decision.response_text
    assert decision.prompt_summary  # coordinate-free summary for the transcript


def test_invalid_response_marks_parse_failure(visible_obs):
    agent = LlmAgent(_StubProvider("I am still thinking, no decision yet."))
    decision = agent.decide(visible_obs, None, "cop")
    assert decision.parsed_ok is False
    assert decision.parse_error == "no_action_line"
