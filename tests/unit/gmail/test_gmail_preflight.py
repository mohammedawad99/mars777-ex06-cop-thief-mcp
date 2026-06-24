"""Unit tests for the Gmail OAuth external-file readiness preflight.

No Gmail API is called and no file contents are read: the preflight checks only
existence and location, and its result never carries credential/token contents.
"""

from pathlib import Path

from mars777_cop_thief.gmail import preflight

_ENV_KEYS = ("GOOGLE_OAUTH_CLIENT_SECRETS", "GOOGLE_OAUTH_TOKEN_PATH")


def _outside_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A fake repo root plus credentials/token files that live OUTSIDE it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    external = tmp_path / "private"
    external.mkdir()
    creds = external / "credentials.json"
    token = external / "token.json"
    creds.write_text("FAKE-SECRET-CLIENT-ID-do-not-leak", encoding="utf-8")
    token.write_text("FAKE-REFRESH-TOKEN-do-not-leak", encoding="utf-8")
    return repo, creds, token


def test_gmail_preflight_ready_when_files_exist_outside_repo(tmp_path):
    repo, creds, token = _outside_files(tmp_path)
    env = {_ENV_KEYS[0]: str(creds), _ENV_KEYS[1]: str(token), "RUN_GMAIL_LIVE": "0"}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["status"] == "ready"
    assert result["credentials_file_exists"] is True
    assert result["token_file_exists"] is True
    assert result["outside_repo"] is True
    assert result["live_send_enabled"] is False
    assert result["blockers"] == []


def test_gmail_preflight_missing_credentials_is_blocker(tmp_path):
    repo, _creds, token = _outside_files(tmp_path)
    env = {_ENV_KEYS[0]: str(tmp_path / "private" / "nope.json"), _ENV_KEYS[1]: str(token)}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["status"] == "blocked"
    assert result["credentials_file_exists"] is False
    assert any("client-secrets file does not exist" in b for b in result["blockers"])


def test_gmail_preflight_missing_token_is_blocker(tmp_path):
    repo, creds, _token = _outside_files(tmp_path)
    env = {_ENV_KEYS[0]: str(creds)}  # token env var unset entirely
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["status"] == "blocked"
    assert result["token_file_exists"] is False
    assert any("token path env var is not set" in b for b in result["blockers"])


def test_gmail_preflight_path_inside_repo_is_blocker(tmp_path):
    repo, _creds, _token = _outside_files(tmp_path)
    inside = repo / "credentials.json"
    inside.write_text("x", encoding="utf-8")
    env = {_ENV_KEYS[0]: str(inside), _ENV_KEYS[1]: str(inside)}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["outside_repo"] is False
    assert any("INSIDE the repository" in b for b in result["blockers"])


def test_gmail_preflight_warns_on_unexpected_filename(tmp_path):
    repo, _creds, _token = _outside_files(tmp_path)
    alt = tmp_path / "private" / "client_secret_alt.json"
    alt.write_text("x", encoding="utf-8")
    tok = tmp_path / "private" / "oauth_token_alt.json"
    tok.write_text("x", encoding="utf-8")
    env = {_ENV_KEYS[0]: str(alt), _ENV_KEYS[1]: str(tok)}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["status"] == "ready"  # safe alternatives still pass, but warn
    assert len(result["warnings"]) == 2


def test_gmail_preflight_does_not_read_file_contents(tmp_path, monkeypatch):
    repo, creds, token = _outside_files(tmp_path)
    guarded = {creds.resolve(), token.resolve()}
    real_read_text = Path.read_text
    real_open = Path.open

    def _guard(real):
        def wrapper(self, *args, **kwargs):
            if Path(self).resolve() in guarded:
                raise AssertionError("preflight must not open OAuth file contents")
            return real(self, *args, **kwargs)

        return wrapper

    monkeypatch.setattr(Path, "read_text", _guard(real_read_text))
    monkeypatch.setattr(Path, "open", _guard(real_open))
    env = {_ENV_KEYS[0]: str(creds), _ENV_KEYS[1]: str(token), "RUN_GMAIL_LIVE": "1"}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    assert result["status"] == "ready"
    assert result["live_send_enabled"] is True


def test_gmail_preflight_result_contains_no_secret_contents(tmp_path):
    repo, creds, token = _outside_files(tmp_path)
    env = {_ENV_KEYS[0]: str(creds), _ENV_KEYS[1]: str(token)}
    result = preflight.run_gmail_preflight(env=env, root=repo)
    import json

    blob = json.dumps(result)
    assert "FAKE-SECRET-CLIENT-ID" not in blob
    assert "FAKE-REFRESH-TOKEN" not in blob
