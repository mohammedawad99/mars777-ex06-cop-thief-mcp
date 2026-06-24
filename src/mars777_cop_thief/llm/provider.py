"""Provider-agnostic LLM interface and response type.

The provider lives on the orchestrator/client side, never inside the MCP
servers. ``LlmResponse.metadata`` must never carry secrets or API keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LlmResponse:
    """A single provider completion plus token/cost accounting."""

    text: str
    provider_name: str
    model_name: str
    prompt_tokens_estimate: int
    response_tokens_estimate: int
    estimated_cost_usd: float
    metadata: dict


class LlmProvider(Protocol):
    """Minimal completion interface implemented by any provider."""

    provider_name: str
    model_name: str

    def complete(self, prompt: str, *, role: str, context: dict) -> LlmResponse:  # pragma: no cover
        """Return a completion for ``prompt`` given the role and context."""
        ...
