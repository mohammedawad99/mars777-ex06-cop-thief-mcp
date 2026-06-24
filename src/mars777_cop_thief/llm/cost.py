"""Token and cost accounting for prompts/responses.

Estimates are rough (character-based) and provider-agnostic. The fake_local
provider has a zero rate — it does no real spend — but token counts are still
computed and summed so the accounting model is real and ready for a paid
provider that sets a non-zero rate.
"""

from __future__ import annotations

FAKE_LOCAL_RATE_PER_1K = 0.0  # fake_local has no real spend
_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Rough non-negative token estimate (~4 characters per token)."""
    if not text:
        return 0
    return max(1, (len(text) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN)


def estimate_cost(prompt_tokens: int, response_tokens: int, rate_per_1k: float) -> float:
    """Non-negative USD estimate from token counts and a per-1k rate."""
    total = max(0, prompt_tokens) + max(0, response_tokens)
    return round(total / 1000.0 * max(0.0, rate_per_1k), 6)
