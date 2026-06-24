"""LLM agent: build a prompt, call the provider, parse the action.

The agent ties together the prompt builder, a provider, and the parser, and
returns a structured decision (including parse status and token/cost estimates).
It performs no fallback itself — the trusted orchestrator decides what to do when
parsing fails or the action is illegal.
"""

from __future__ import annotations

from dataclasses import dataclass

from mars777_cop_thief.llm.parser import parse_action
from mars777_cop_thief.llm.prompts import build_prompt


@dataclass(frozen=True)
class AgentDecision:
    """A single agent turn: parsed action plus provider accounting."""

    role: str
    parsed_ok: bool
    action_type: str | None
    direction: str | None
    parse_error: str | None
    response_text: str
    prompt_summary: str
    prompt_tokens_estimate: int
    response_tokens_estimate: int
    estimated_cost_usd: float


def _summarize(prompt: str) -> str:
    """Short, coordinate-free prompt summary for the transcript (first two lines)."""
    return "\n".join(prompt.splitlines()[:2])


class LlmAgent:
    """Drives one provider for either role; stateless across turns."""

    def __init__(self, provider) -> None:
        self.provider = provider

    def decide(self, observation: dict, message, role: str) -> AgentDecision:
        """Return a structured decision for ``role`` given a role-safe observation."""
        prompt = build_prompt(observation, message, role)
        response = self.provider.complete(
            prompt, role=role, context={"observation": observation, "message": message}
        )
        parsed = parse_action(response.text, role)
        return AgentDecision(
            role=role,
            parsed_ok=parsed.ok,
            action_type=parsed.action_type,
            direction=parsed.direction,
            parse_error=parsed.error,
            response_text=response.text,
            prompt_summary=_summarize(prompt),
            prompt_tokens_estimate=response.prompt_tokens_estimate,
            response_tokens_estimate=response.response_tokens_estimate,
            estimated_cost_usd=response.estimated_cost_usd,
        )
