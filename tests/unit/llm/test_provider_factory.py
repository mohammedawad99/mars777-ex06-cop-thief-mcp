"""Unit tests for the env-driven provider factory (no network)."""

import pytest

from mars777_cop_thief.llm.config import LlmConfigError, load_llm_config
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.gemini_provider import GeminiProvider
from mars777_cop_thief.llm.provider_factory import create_provider_from_env


@pytest.fixture
def config() -> dict:
    return load_llm_config()


def test_default_is_fake_local(config):
    provider = create_provider_from_env(config, env={})
    assert isinstance(provider, FakeLocalProvider)
    assert provider.provider_name == "fake_local"


def test_selects_gemini_only_when_requested(config):
    env = {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "fake-gemini-key"}
    provider = create_provider_from_env(config, env=env)
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"
    assert provider.model_name == config["default_gemini_model"]


def test_gemini_requested_without_key_raises(config):
    with pytest.raises(LlmConfigError):
        create_provider_from_env(config, env={"LLM_PROVIDER": "gemini"})


def test_google_api_key_is_accepted(config):
    env = {
        "LLM_PROVIDER": "gemini",
        "GOOGLE_API_KEY": "fake-gemini-key",
        "GEMINI_MODEL": "gemini-x",
    }
    provider = create_provider_from_env(config, env=env)
    assert isinstance(provider, GeminiProvider)
    assert provider.model_name == "gemini-x"


def test_unknown_provider_raises(config):
    with pytest.raises(LlmConfigError):
        create_provider_from_env(config, env={"LLM_PROVIDER": "openai"})


def test_default_config_loads_allowed_providers():
    config = load_llm_config()
    assert config["provider"] == "fake_local"
    assert config["allowed_providers"] == ["fake_local", "gemini"]
    assert config["live_smoke_enabled_env_var"] == "RUN_GEMINI_LIVE"
