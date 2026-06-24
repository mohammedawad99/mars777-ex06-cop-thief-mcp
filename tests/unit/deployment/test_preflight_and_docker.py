"""Unit tests for the deployment preflight and Docker static checks."""

from pathlib import Path

from mars777_cop_thief.deployment import preflight
from mars777_cop_thief.deployment.docker_checks import (
    REQUIRED_DOCKERIGNORE,
    find_forbidden_secret_files,
    missing_dockerignore_entries,
)

_ROOT = Path(__file__).resolve().parents[3]


def test_preflight_passes_on_real_repo():
    result = preflight.run_preflight()
    assert result["passed"] is True
    assert result["status"] == "ok"
    assert result["cloud_status"] == "not_deployed"
    assert all(result["checks"].values())


def test_preflight_detects_missing_dockerfile(tmp_path):
    # An empty tree has no Dockerfile/.dockerignore → packaging not ready.
    result = preflight.run_preflight(root=tmp_path)
    assert result["passed"] is False
    assert result["checks"]["dockerfile_present"] is False
    assert result["checks"]["dockerignore_present"] is False


def test_preflight_rejects_forbidden_secret_file(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11-slim\n", encoding="utf-8")
    (tmp_path / ".dockerignore").write_text("\n".join(REQUIRED_DOCKERIGNORE), encoding="utf-8")
    (tmp_path / "credentials.json").write_text("{}", encoding="utf-8")
    result = preflight.run_preflight(root=tmp_path)
    assert result["checks"]["no_forbidden_secret_files"] is False
    assert result["passed"] is False


def test_real_dockerignore_covers_required_entries():
    assert missing_dockerignore_entries(_ROOT) == []
    for required in (".env", "credentials.json", "token.json", ".venv", "__pycache__", ".coverage"):
        assert required in REQUIRED_DOCKERIGNORE


def test_find_forbidden_secret_files_detects_keys(tmp_path):
    (tmp_path / "token.json").write_text("{}", encoding="utf-8")
    (tmp_path / "deploy.key").write_text("x", encoding="utf-8")
    (tmp_path / "ok.txt").write_text("fine", encoding="utf-8")
    found = find_forbidden_secret_files(tmp_path)
    assert "token.json" in found
    assert "deploy.key" in found
    assert "ok.txt" not in found


def test_preflight_main_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(preflight, "run_preflight", lambda: {"passed": True, "checks": {}})
    assert preflight.main() == 0
    assert "passed" in capsys.readouterr().out


def test_preflight_main_returns_one(monkeypatch):
    monkeypatch.setattr(preflight, "run_preflight", lambda: {"passed": False})
    assert preflight.main() == 1
