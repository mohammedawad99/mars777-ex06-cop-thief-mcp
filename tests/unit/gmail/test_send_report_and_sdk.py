"""Unit tests for the send_report CLI and SDK Gmail delegation (no network)."""

import json

from mars777_cop_thief.gmail import send_report
from mars777_cop_thief.sdk import AssignmentSdk


def test_run_send_dry_run_when_not_live(report):
    result = send_report.run_send(env={}, report=report)
    assert result["status"] == "dry_run"
    assert result["body_json_valid"] is True
    assert result["gmail_message_id"] is None


def test_run_send_live_without_credentials_fails(report):
    result = send_report.run_send(env={"RUN_GMAIL_LIVE": "1"}, report=report)
    assert result["status"] == "failed"
    assert "client secrets" in result["error_message"]


def test_default_report_loads_evidence_example():
    result = send_report.run_send(env={})  # no report → loads the committed example
    assert result["status"] == "dry_run"
    assert result["report_type"] == "internal_game"


def test_main_skips_dry_run_with_exit_zero(monkeypatch, capsys):
    monkeypatch.delenv("RUN_GMAIL_LIVE", raising=False)
    assert send_report.main() == 0
    out = capsys.readouterr().out
    assert json.loads(out)["status"] == "dry_run"


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(send_report, "run_send", lambda: {"status": "failed"})
    assert send_report.main() == 1


def test_sdk_dry_run_and_message_helpers(report):
    sdk = AssignmentSdk()
    assert sdk.dry_run_gmail_report(report, env={})["status"] == "dry_run"
    raw = sdk.build_gmail_report_message(report, env={})
    assert sdk.validate_gmail_message_body(raw) == report
