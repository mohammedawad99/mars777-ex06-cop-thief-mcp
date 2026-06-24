"""Unit tests for failure classification, retry policy, and resource guard."""

from pathlib import Path

import pytest

from mars777_cop_thief.gmail.config import GmailConfigError
from mars777_cop_thief.run.rate_limit import ResourceGuard
from mars777_cop_thief.run.retry import RetryPolicy, retry_call
from mars777_cop_thief.run.status import FailureCategory, RunStatus, classify_exception, redact
from mars777_cop_thief.shared.config import ConfigError, load_json_config

_RUNTIME = Path(__file__).resolve().parents[3] / "config" / "runtime.default.json"


class _CustomAuthError(RuntimeError):
    pass


def test_classifier_maps_config_errors():
    assert classify_exception(ConfigError("bad")) is FailureCategory.CONFIG_ERROR
    assert classify_exception(GmailConfigError("bad")) is FailureCategory.CONFIG_ERROR


def test_classifier_maps_auth_errors():
    assert classify_exception(_CustomAuthError("nope")) is FailureCategory.AUTH_ERROR


def test_classifier_maps_timeout_and_unknown():
    assert classify_exception(TimeoutError("slow")) is FailureCategory.TIMEOUT
    assert classify_exception(ValueError("???")) is FailureCategory.UNKNOWN


def test_redact_strips_dummy_token():
    assert "dummy-local-cop-token" not in redact("leaked dummy-local-cop-token here")


def test_run_status_failed_classifies_and_redacts():
    status = RunStatus.failed(ConfigError("bad config")).to_dict()
    assert status["ok"] is False
    assert status["category"] == "config_error"
    assert status["message"] == "bad config"


def test_retry_policy_from_runtime_config():
    policy = RetryPolicy.from_config(load_json_config(_RUNTIME))
    assert policy.validate() == []
    assert policy.max_retries == 2


def test_retry_policy_validates_bounds():
    assert RetryPolicy(2, 0.5, 1, 1, 1).validate() == []
    errors = RetryPolicy(-1, -1, 0, 0, 0).validate()
    assert len(errors) == 5  # max_retries, backoff, and three timeouts


_POLICY = RetryPolicy(
    max_retries=2, backoff_seconds=0.0, connect_timeout=1, call_timeout=1, readiness_timeout=1
)


def test_retry_succeeds_after_transient_failures():
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient")
        return "ok"

    assert retry_call(flaky, _POLICY, sleep=lambda *_: None) == "ok"
    assert attempts["n"] == 3


def test_retry_stops_at_max_retries():
    attempts = {"n": 0}

    def always_fail():
        attempts["n"] += 1
        raise RuntimeError("transient")

    with pytest.raises(RuntimeError):
        retry_call(always_fail, _POLICY, sleep=lambda *_: None)
    assert attempts["n"] == 3  # initial + 2 retries


def test_retry_does_not_retry_non_transient():
    attempts = {"n": 0}

    def fail_once():
        attempts["n"] += 1
        raise ValueError("permanent")

    with pytest.raises(ValueError):
        retry_call(fail_once, _POLICY, is_transient=lambda exc: False, sleep=lambda *_: None)
    assert attempts["n"] == 1


def test_resource_guard_from_configs_and_validation():
    guard = ResourceGuard.from_configs(
        {"defaults": {"mcp_requests_per_minute": 60, "mcp_max_concurrent": 4}},
        {"provider_max_output_tokens": 120},
    )
    assert guard.validate() == []
    assert ResourceGuard(0, 0, 0).validate()
