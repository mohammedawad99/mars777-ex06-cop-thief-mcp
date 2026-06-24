"""Unit tests for the read-only cloud readiness and combined live-readiness.

No real gcloud, cloud, or Gmail command is ever executed: the CLI lookup and the
command runner are injected, so every check runs offline against fakes.
"""

import json
from pathlib import Path

from mars777_cop_thief.deployment import gcloud_checks, live_readiness

_ROOT = Path(__file__).resolve().parents[3]
_INSTALLED = lambda _name: "/usr/bin/gcloud"  # noqa: E731 - tiny test stub
_MISSING = lambda _name: None  # noqa: E731 - tiny test stub


def _runner(account="user@example.com", project="api-mars-777", billing="True"):
    """A fake gcloud runner — never touches the network or a real CLI."""

    def run(args):
        if "auth" in args:
            return account
        if "config" in args:
            return project
        if "billing" in args:
            return billing
        return None  # pragma: no cover - no other command is issued

    return run


def test_cloud_missing_gcloud_is_blocker():
    result = gcloud_checks.check_cloud_readiness({}, which=_MISSING, runner=_runner())
    assert result["gcloud_installed"] is False
    assert result["status"] == "blocked"
    assert any("gcloud CLI not found" in b for b in result["blockers"])


def test_cloud_parses_mocked_account_and_project():
    env = {"CLOUD_RUN_REGION": "me-west1"}
    result = gcloud_checks.check_cloud_readiness(env, which=_INSTALLED, runner=_runner())
    assert result["gcloud_installed"] is True
    assert result["authenticated"] is True
    assert result["active_account_present"] is True
    assert result["active_project"] == "api-mars-777"
    assert result["project_matches"] is True
    assert result["intended_region"] == "me-west1"
    assert result["region_source"] == "env:CLOUD_RUN_REGION"
    assert result["billing_enabled"] is True
    assert result["status"] == "ready"
    assert result["public_urls_deployed"] is False


def test_cloud_project_mismatch_is_blocker():
    runner = _runner(project="some-other-project")
    result = gcloud_checks.check_cloud_readiness({}, which=_INSTALLED, runner=runner)
    assert result["project_matches"] is False
    assert any("!= expected" in b for b in result["blockers"])
    assert result["intended_region"] == gcloud_checks.RECOMMENDED_REGION  # fallback default


def test_cloud_billing_disabled_is_blocker():
    runner = _runner(billing="False")
    result = gcloud_checks.check_cloud_readiness({}, which=_INSTALLED, runner=runner)
    assert result["billing_enabled"] is False
    assert any("billing is disabled" in b for b in result["blockers"])


def test_cloud_billing_unknown_is_warning_not_crash():
    runner = _runner(billing=None)
    result = gcloud_checks.check_cloud_readiness({}, which=_INSTALLED, runner=runner)
    assert result["billing_enabled"] is None
    assert any("billing status unknown" in w for w in result["warnings"])
    assert result["status"] == "ready"  # unknown billing does not block by itself


def test_cloud_not_authenticated_and_unknown_project():
    runner = _runner(account="", project="")
    result = gcloud_checks.check_cloud_readiness({}, which=_INSTALLED, runner=runner)
    assert result["authenticated"] is False
    assert result["active_project"] is None
    assert result["project_matches"] is None
    assert any("no active gcloud account" in b for b in result["blockers"])
    assert any("project unknown" in w for w in result["warnings"])


def _live(tmp_path, *, which, runner):
    external = tmp_path / "private"
    external.mkdir()
    creds = external / "credentials.json"
    token = external / "token.json"
    creds.write_text("SECRET", encoding="utf-8")
    token.write_text("SECRET", encoding="utf-8")
    env = {
        "GOOGLE_OAUTH_CLIENT_SECRETS": str(creds),
        "GOOGLE_OAUTH_TOKEN_PATH": str(token),
        "CLOUD_RUN_REGION": "me-west1",
        "RUN_GMAIL_LIVE": "0",
        "RUN_CLOUD_DEPLOY": "0",
    }
    return live_readiness.run_live_readiness(env=env, root=_ROOT, which=which, runner=runner)


def test_combined_ready_path_is_json_serializable(tmp_path):
    result = _live(tmp_path, which=_INSTALLED, runner=_runner())
    json.dumps(result)  # must not raise
    assert result["status"] == "ok"
    assert result["ready_for_live"] is True
    assert result["live_send_attempted"] is False
    assert result["cloud_deploy_attempted"] is False
    assert result["remaining_manual_actions"]  # always lists manual deploy steps


def test_combined_blocked_path_lists_manual_actions(tmp_path):
    result = _live(tmp_path, which=_MISSING, runner=_runner())
    assert result["ready_for_live"] is False
    assert any("install the gcloud CLI" in a for a in result["remaining_manual_actions"])
    assert any("gcloud CLI not found" in b for b in result["blockers"])


def test_combined_report_includes_no_secrets(tmp_path):
    result = _live(tmp_path, which=_INSTALLED, runner=_runner())
    blob = json.dumps(result)
    for needle in ("SECRET", "credentials.json", "token.json", "user@example.com"):
        assert needle not in blob


def test_combined_lists_every_manual_action_when_blocked(tmp_path):
    # gmail blocked (missing creds), gcloud installed but unauthenticated, project
    # unknown, billing unknown -> every conditional manual action fires.
    external = tmp_path / "private"
    external.mkdir()
    token = external / "token.json"
    token.write_text("x", encoding="utf-8")
    env = {
        "GOOGLE_OAUTH_CLIENT_SECRETS": str(external / "missing.json"),
        "GOOGLE_OAUTH_TOKEN_PATH": str(token),
        "RUN_GMAIL_LIVE": "0",
    }
    runner = _runner(account="", project="", billing=None)
    result = live_readiness.run_live_readiness(env=env, root=_ROOT, which=_INSTALLED, runner=runner)
    actions = result["remaining_manual_actions"]
    assert any("place valid OAuth files" in a for a in actions)
    assert any("gcloud auth login" in a for a in actions)
    assert any("select project" in a for a in actions)
    assert any("enable billing" in a for a in actions)
    assert result["ready_for_live"] is False


def test_combined_flags_packaging_not_passing(tmp_path):
    external = tmp_path / "private"
    external.mkdir()
    creds = external / "credentials.json"
    token = external / "token.json"
    creds.write_text("x", encoding="utf-8")
    token.write_text("x", encoding="utf-8")
    fake_root = tmp_path / "fakerepo"  # empty -> packaging preflight cannot pass
    fake_root.mkdir()
    env = {"GOOGLE_OAUTH_CLIENT_SECRETS": str(creds), "GOOGLE_OAUTH_TOKEN_PATH": str(token)}
    result = live_readiness.run_live_readiness(
        env=env, root=fake_root, which=_INSTALLED, runner=_runner()
    )
    assert result["packaging_preflight"]["passed"] is False
    assert any("packaging preflight is not passing" in b for b in result["blockers"])


def test_live_readiness_main_exits_zero_with_blockers(monkeypatch, capsys):
    monkeypatch.setattr(
        live_readiness,
        "run_live_readiness",
        lambda env=None: {"status": "ok", "blockers": ["x"]},
    )
    assert live_readiness.main() == 0
    assert "blockers" in capsys.readouterr().out
