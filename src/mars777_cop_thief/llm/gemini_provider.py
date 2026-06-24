"""Optional real Google Gemini provider (official ``google-genai`` SDK).

Implements the Stage 9 provider interface. The API key is supplied by the factory
from the environment and held privately — it is never logged, returned, or placed
in metadata. Uses a single non-streaming text call with a small output cap and no
tool calling, and falls back to token estimates when usage metadata is absent.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from mars777_cop_thief.llm.cost import estimate_cost, estimate_tokens
from mars777_cop_thief.llm.provider import LlmResponse

# Placeholder blended rate; set to your tier's $/1k tokens to price real runs.
GEMINI_RATE_PER_1K = 0.0


def _build_client(api_key: str):
    return genai.Client(api_key=api_key)


def _build_config(max_output_tokens: int, temperature: float):
    return types.GenerateContentConfig(max_output_tokens=max_output_tokens, temperature=temperature)


def _usage_tokens(response, prompt: str, text: str) -> tuple[int, int, str]:
    usage = getattr(response, "usage_metadata", None)
    prompt_count = getattr(usage, "prompt_token_count", None) if usage else None
    response_count = getattr(usage, "candidates_token_count", None) if usage else None
    if prompt_count is not None and response_count is not None:
        return max(0, int(prompt_count)), max(0, int(response_count)), "actual"
    return estimate_tokens(prompt), estimate_tokens(text), "estimate"


class GeminiProvider:
    """Calls Gemini via google-genai; conforms to the LlmProvider interface."""

    provider_name = "gemini"

    def __init__(self, *, api_key, model, max_output_tokens=120, temperature=0.2, client=None):
        self._api_key = api_key  # private; never logged or returned
        self.model_name = model
        self._max_output_tokens = int(max_output_tokens)
        self._temperature = float(temperature)
        self._client = client if client is not None else _build_client(api_key)

    def complete(self, prompt: str, *, role: str, context: dict) -> LlmResponse:
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=_build_config(self._max_output_tokens, self._temperature),
        )
        text = (getattr(response, "text", None) or "").strip()
        prompt_tokens, response_tokens, usage_source = _usage_tokens(response, prompt, text)
        return LlmResponse(
            text=text,
            provider_name=self.provider_name,
            model_name=self.model_name,
            prompt_tokens_estimate=prompt_tokens,
            response_tokens_estimate=response_tokens,
            estimated_cost_usd=estimate_cost(prompt_tokens, response_tokens, GEMINI_RATE_PER_1K),
            metadata={"llm_mode": "gemini", "usage_source": usage_source},
        )
