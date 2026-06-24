"""Tests for the evidence generator CLI and SDK delegation (no real servers)."""

import json

from mars777_cop_thief.reporting import generate_evidence_pack as gen
from mars777_cop_thief.reporting.evidence import REPORT_FILE
from mars777_cop_thief.sdk import AssignmentSdk


def test_generate_writes_valid_pack(tmp_path, mcp_report):
    result = gen.generate(directory=tmp_path, mcp_report=mcp_report)
    assert result["validation_status"] == "valid"
    assert result["validation_errors"] == []
    assert (tmp_path / REPORT_FILE).is_file()


def test_generate_defaults_to_run_game_smoke(tmp_path, mcp_report, monkeypatch):
    monkeypatch.setattr(gen, "run_game_smoke", lambda: dict(mcp_report))
    result = gen.generate(directory=tmp_path)
    assert result["validation_status"] == "valid"


def test_main_returns_zero_on_valid(monkeypatch, capsys):
    monkeypatch.setattr(
        gen,
        "generate",
        lambda: {"validation_status": "valid", "validation_errors": [], "files": {}},
    )
    assert gen.main() == 0
    assert "validation_status" in capsys.readouterr().out


def test_main_returns_one_on_invalid(monkeypatch):
    monkeypatch.setattr(
        gen,
        "generate",
        lambda: {"validation_status": "invalid", "validation_errors": ["x"], "files": {}},
    )
    assert gen.main() == 1


def test_sdk_validates_and_builds_report(mcp_report):
    sdk = AssignmentSdk()
    report = sdk.build_official_internal_report(mcp_report)
    assert report["report_type"] == "internal_game"
    assert sdk.validate_internal_report(report) == []
    assert json.dumps(report)


def test_sdk_generate_evidence_delegates(tmp_path, mcp_report, monkeypatch):
    monkeypatch.setattr(
        "mars777_cop_thief.sdk.sdk.generate_evidence",
        lambda directory=None: {"validation_status": "valid", "dir": str(directory)},
    )
    result = AssignmentSdk().generate_local_evidence_pack(directory=tmp_path)
    assert result["validation_status"] == "valid"
