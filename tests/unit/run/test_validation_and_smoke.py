"""Unit tests for aggregate validation, hardened smoke, and SDK delegation."""

import json

from mars777_cop_thief.run import hardened_smoke
from mars777_cop_thief.run.hardened_smoke import _json_ok, run_hardened_smoke
from mars777_cop_thief.run.identity import build_run_identity
from mars777_cop_thief.run.manifest import build_manifest
from mars777_cop_thief.run.validation import validate_full_report
from mars777_cop_thief.sdk import AssignmentSdk


def _manifest(cloud_status: str):
    identity = build_run_identity(
        {"group_slug": "mars777"},
        stage="hardened",
        mode="m",
        created_at_utc="t",
        git_commit="g",
        cloud_status=cloud_status,
    )
    return build_manifest(identity, {}, validation_gates={})


def test_valid_full_report_accepted(official_report):
    assert validate_full_report(official_report) == []


def test_rejects_wrong_sub_game_count(official_report):
    official_report["sub_games"] = official_report["sub_games"][:1]
    errors = validate_full_report(official_report)
    assert any("expected 2 sub-games" in e for e in errors)


def test_rejects_totals_mismatch(official_report):
    official_report["sub_games"][0]["cop_score"] += 7
    assert any("cop totals mismatch" in e for e in validate_full_report(official_report))


def test_rejects_token_like_content(official_report):
    official_report["evidence"]["auth_token"] = "x"
    assert any("forbidden" in e for e in validate_full_report(official_report))


def test_rejects_missing_status_field(official_report):
    del official_report["email_status"]
    errors = validate_full_report(official_report)
    assert any("missing status field: email_status" in e for e in errors)


def test_rejects_invalid_sub_games(official_report):
    official_report["totals"]["invalid_sub_games"] = 1
    assert any("invalid sub-games present" in e for e in validate_full_report(official_report))


def test_rejects_missing_outcome_reason(official_report):
    del official_report["sub_games"][0]["outcome_reason"]
    assert any("missing outcome_reason" in e for e in validate_full_report(official_report))


def test_rejects_local_url_when_cloud_not_local(official_report):
    official_report["cloud_status"] = "deployed"  # but URLs are still 127.0.0.1
    assert any("local URL not allowed" in e for e in validate_full_report(official_report))


def test_manifest_cloud_status_mismatch_rejected(official_report):
    errors = validate_full_report(official_report, _manifest("deployed"))
    assert any("manifest cloud_status" in e for e in errors)


def test_manifest_cloud_status_match_passes(official_report):
    errors = validate_full_report(official_report, _manifest("not_deployed"))
    assert not any("manifest cloud_status" in e for e in errors)


def test_hardened_smoke_summary_is_serializable(prompted_report):
    summary = run_hardened_smoke(
        prompted_report=prompted_report, env={}, created_at_utc="t", git_commit="g"
    )
    assert json.dumps(summary)
    assert summary["passed"] is True
    assert summary["status"] == "ok"
    assert all(summary["checks"].values())
    assert summary["report_validation_errors"] == []


def test_hardened_smoke_fails_on_bad_report(prompted_report):
    prompted_report["sub_games"][0]["winner"] = "nobody"  # invalid winner
    summary = run_hardened_smoke(
        prompted_report=prompted_report, env={}, created_at_utc="t", git_commit="g"
    )
    assert summary["passed"] is False
    assert summary["checks"]["report_valid"] is False


def test_sdk_build_run_manifest_and_validate(prompted_report, official_report):
    sdk = AssignmentSdk()
    manifest = sdk.build_run_manifest(prompted_report["config"], created_at_utc="t", git_commit="g")
    assert json.dumps(manifest)
    assert manifest["run_identity"]["stage"] == "hardened"
    assert sdk.validate_full_report(official_report) == []


def test_sdk_run_hardened_local_smoke_delegates(monkeypatch):
    monkeypatch.setattr(
        "mars777_cop_thief.sdk.sdk.run_hardened_smoke",
        lambda num_sub_games=None: {"passed": True, "n": num_sub_games},
    )
    assert AssignmentSdk().run_hardened_local_smoke()["passed"] is True


def test_json_ok_detects_non_serializable():
    assert _json_ok({"a": 1}) is True
    assert _json_ok({"a": {1, 2, 3}}) is False  # a set is not JSON serializable


def test_main_returns_exit_codes(monkeypatch, capsys):
    monkeypatch.setattr(
        hardened_smoke, "run_hardened_smoke", lambda: {"passed": True, "checks": {}}
    )
    assert hardened_smoke.main() == 0
    assert "passed" in capsys.readouterr().out
    monkeypatch.setattr(hardened_smoke, "run_hardened_smoke", lambda: {"passed": False})
    assert hardened_smoke.main() == 1
