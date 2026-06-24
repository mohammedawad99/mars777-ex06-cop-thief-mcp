"""Unit tests for Gmail credential loading (injected deps; no real files)."""

import pytest

from mars777_cop_thief.gmail.auth import GmailAuthError, _AuthDeps, load_credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class _Creds:
    def __init__(self, valid=True, expired=False, refresh_token=None):
        self.valid = valid
        self.expired = expired
        self.refresh_token = refresh_token


def _deps(*, exists=(), token=None, flow=None, events=None):
    events = events if events is not None else []
    return _AuthDeps(
        path_exists=lambda p: p in exists,
        load_token=lambda token_path, scopes: token,
        refresh=lambda creds: events.append("refresh"),
        save_token=lambda token_path, creds: events.append("save"),
        run_flow=lambda creds_path, scopes: flow,
    )


def test_valid_token_is_returned():
    creds = _Creds(valid=True)
    deps = _deps(exists={"/t/token.json"}, token=creds)
    out = load_credentials("/c/creds.json", "/t/token.json", SCOPES, run_auth=False, deps=deps)
    assert out is creds


def test_expired_token_is_refreshed_and_saved():
    creds = _Creds(valid=False, expired=True, refresh_token="r")
    events = []
    deps = _deps(exists={"/t/token.json"}, token=creds, events=events)
    out = load_credentials("/c/creds.json", "/t/token.json", SCOPES, run_auth=False, deps=deps)
    assert out is creds
    assert events == ["refresh", "save"]


def test_missing_credentials_raises():
    deps = _deps(exists=set())
    with pytest.raises(GmailAuthError, match="client secrets"):
        load_credentials(None, None, SCOPES, run_auth=True, deps=deps)


def test_token_missing_without_auth_flag_raises():
    deps = _deps(exists={"/c/creds.json"})
    with pytest.raises(GmailAuthError, match="RUN_GMAIL_AUTH"):
        load_credentials("/c/creds.json", "/t/token.json", SCOPES, run_auth=False, deps=deps)


def test_invalid_non_refreshable_token_falls_through():
    creds = _Creds(valid=False, expired=False, refresh_token=None)
    deps = _deps(exists={"/t/token.json"}, token=creds)  # token present but unusable
    with pytest.raises(GmailAuthError, match="client secrets"):
        load_credentials(None, "/t/token.json", SCOPES, run_auth=True, deps=deps)


def test_oauth_flow_runs_when_enabled():
    flow_creds = _Creds(valid=True)
    events = []
    deps = _deps(exists={"/c/creds.json"}, flow=flow_creds, events=events)
    out = load_credentials("/c/creds.json", "/t/token.json", SCOPES, run_auth=True, deps=deps)
    assert out is flow_creds
    assert events == ["save"]
