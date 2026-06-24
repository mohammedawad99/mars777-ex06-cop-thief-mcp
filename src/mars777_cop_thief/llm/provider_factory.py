"""Select an LLM provider from configuration and the environment.

Default is the offline ``fake_local`` provider. Gemini is opt-in via
``LLM_PROVIDER=gemini`` with an API key present in the environment. No import-time
API calls are made; a missing key for a requested Gemini provider raises a
controlled :class:`LlmConfigError`.
"""

from __future__ import annotations

import os

from mars777_cop_thief.llm.config import LlmConfigError, load_llm_config
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.gemini_provider import GeminiProvider


def _api_key(config: dict, env) -> str | None:
    return env.get(config["gemini_api_key_env_var"]) or env.get(config["google_api_key_env_var"])


def build_gemini_provider(config: dict, env, client=None) -> GeminiProvider:
    """Build a Gemini provider from env; raise if no API key is present."""
    api_key = _api_key(config, env)
    if not api_key:
        raise LlmConfigError(
            "gemini provider selected but no API key in "
            f"{config['gemini_api_key_env_var']}/{config['google_api_key_env_var']}"
        )
    model = env.get(config["gemini_model_env_var"]) or config["default_gemini_model"]
    max_out = int(env.get(config["max_output_tokens_env_var"]) or config["max_output_tokens"])
    temperature = float(env.get(config["temperature_env_var"]) or config["temperature"])
    return GeminiProvider(
        api_key=api_key,
        model=model,
        max_output_tokens=max_out,
        temperature=temperature,
        client=client,
    )


def create_provider_from_env(config: dict | None = None, env=None):
    """Return the configured provider (default ``fake_local``)."""
    config = config if config is not None else load_llm_config()
    env = env if env is not None else os.environ
    name = env.get(config["provider_env_var"], config["provider"]).strip().lower()
    if name not in config["allowed_providers"]:
        raise LlmConfigError(f"unknown provider: {name}")
    if name == "gemini":
        return build_gemini_provider(config, env)
    return FakeLocalProvider()
