"""Unit tests for the local MCP token auth guard."""

from mars777_cop_thief.mcp_servers.auth import REDACTED, check_auth

ENV = "COP_MCP_TOKEN"


def test_accepts_matching_token(monkeypatch):
    monkeypatch.setenv(ENV, "secret-token")
    assert check_auth("secret-token", ENV) is None


def test_rejects_missing_token(monkeypatch):
    monkeypatch.setenv(ENV, "secret-token")
    result = check_auth(None, ENV)
    assert result["error"] == "unauthorized"
    assert result["reason"] == "invalid_token"


def test_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv(ENV, "secret-token")
    assert check_auth("nope", ENV)["reason"] == "invalid_token"


def test_rejects_when_not_configured(monkeypatch):
    monkeypatch.delenv(ENV, raising=False)
    assert check_auth("anything", ENV)["reason"] == "auth_not_configured"


def test_result_never_reveals_expected_token(monkeypatch):
    monkeypatch.setenv(ENV, "super-secret-value")
    result = check_auth("wrong", ENV)
    assert "super-secret-value" not in str(result)
    assert result["auth_token"] == REDACTED
