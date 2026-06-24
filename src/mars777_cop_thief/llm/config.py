"""LLM provider configuration loading.

Reads ``config/llm.default.json`` (provider selection, env-var names, defaults).
Holds no secrets — only the *names* of the environment variables that carry them.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.shared.config import load_json_config

_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LLM_CONFIG_PATH = _ROOT / "config" / "llm.default.json"


class LlmConfigError(RuntimeError):
    """Raised when an LLM provider is requested but cannot be configured."""


def load_llm_config(path: str | Path | None = None) -> dict:
    """Load the LLM provider configuration JSON."""
    return load_json_config(path or DEFAULT_LLM_CONFIG_PATH)
