"""Unit tests for the Gemini provider adapter (mocked SDK; no network)."""

import json

from mars777_cop_thief.llm.gemini_provider import GeminiProvider

API_KEY = "fake-gemini-key-value"


class _Usage:
    prompt_token_count = 11
    candidates_token_count = 7


class _Response:
    def __init__(self, text, usage=None):
        self.text = text
        self.usage_metadata = usage


class _Models:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        return self._response


class _Client:
    def __init__(self, response):
        self.models = _Models(response)


def _provider(response):
    client = _Client(response)
    return GeminiProvider(api_key=API_KEY, model="gemini-2.5-flash", client=client), client


def test_maps_sdk_response_into_llm_response():
    provider, _ = _provider(_Response("Reasoning. ACTION: move north", _Usage()))
    result = provider.complete("a prompt", role="cop", context={})
    assert result.text == "Reasoning. ACTION: move north"
    assert result.provider_name == "gemini"
    assert result.model_name == "gemini-2.5-flash"
    assert result.prompt_tokens_estimate == 11  # actual usage from the SDK
    assert result.response_tokens_estimate == 7
    assert result.metadata["usage_source"] == "actual"


def test_request_does_not_expose_api_key():
    provider, client = _provider(_Response("ACTION: move east", _Usage()))
    result = provider.complete("the prompt text", role="cop", context={})
    assert API_KEY not in json.dumps(client.models.calls, default=str)
    assert API_KEY not in json.dumps(result.metadata)
    assert "api_key" not in result.metadata


def test_metadata_has_no_secrets():
    provider, _ = _provider(_Response("ACTION: move west", _Usage()))
    metadata = provider.complete("p", role="thief", context={}).metadata
    assert set(metadata) == {"llm_mode", "usage_source"}
    assert metadata["llm_mode"] == "gemini"


def test_malformed_empty_response_is_safe():
    provider, _ = _provider(_Response(None, usage=None))  # no text, no usage
    result = provider.complete("p", role="cop", context={})
    assert result.text == ""  # empty, the ACTION parser will reject → fallback
    assert result.metadata["usage_source"] == "estimate"  # fell back to estimator


def test_token_and_cost_fields_non_negative():
    provider, _ = _provider(_Response("ACTION: move north", _Usage()))
    result = provider.complete("p", role="cop", context={})
    assert result.prompt_tokens_estimate >= 0
    assert result.response_tokens_estimate >= 0
    assert result.estimated_cost_usd >= 0
