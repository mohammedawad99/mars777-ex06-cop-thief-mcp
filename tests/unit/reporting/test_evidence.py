"""Unit tests for the evidence pack writer (writes to a temp directory)."""

import json

import pytest

from mars777_cop_thief.reporting.evidence import (
    REPORT_FILE,
    SUMMARY_FILE,
    TRANSCRIPT_FILE,
    write_evidence_pack,
)
from mars777_cop_thief.reporting.official_report import build_official_internal_report

FORBIDDEN = ("auth_token", "access_token", "refresh_token", "secret", "password", "dummy-local")


def test_writes_expected_files(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    files = write_evidence_pack(tmp_path, official, mcp_report)
    assert set(files) == {REPORT_FILE, SUMMARY_FILE, TRANSCRIPT_FILE}
    for name in files:
        assert (tmp_path / name).is_file()


def test_files_are_valid_json_and_sanitized(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    write_evidence_pack(tmp_path, official, mcp_report)
    for name in (REPORT_FILE, SUMMARY_FILE, TRANSCRIPT_FILE):
        text = (tmp_path / name).read_text(encoding="utf-8")
        json.loads(text)  # valid JSON
        low = text.lower()
        assert not any(pattern in low for pattern in FORBIDDEN)
        assert "54321" not in text and "54322" not in text  # no dynamic ports


def test_report_urls_and_timestamp_normalized(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    write_evidence_pack(tmp_path, official, mcp_report)
    report = json.loads((tmp_path / REPORT_FILE).read_text(encoding="utf-8"))
    assert report["cop_mcp_url"] == "http://127.0.0.1:8001/mcp"
    assert report["thief_mcp_url"] == "http://127.0.0.1:8002/mcp"
    assert report["generated_at_iso"] == "EXAMPLE_GENERATED_AT_UTC"


def test_summary_totals_match_report(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    write_evidence_pack(tmp_path, official, mcp_report)
    report = json.loads((tmp_path / REPORT_FILE).read_text(encoding="utf-8"))
    summary = json.loads((tmp_path / SUMMARY_FILE).read_text(encoding="utf-8"))
    assert summary["totals"] == report["totals"]


def test_writer_refuses_unsanitized_report(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    official["evidence"]["note"] = "accidental auth_token leak"
    with pytest.raises(ValueError):
        write_evidence_pack(tmp_path, official, mcp_report)


def test_transcript_excerpt_is_small(tmp_path, mcp_report):
    official = build_official_internal_report(mcp_report)
    write_evidence_pack(tmp_path, official, mcp_report)
    excerpt = json.loads((tmp_path / TRANSCRIPT_FILE).read_text(encoding="utf-8"))
    assert len(excerpt["messages"]) <= 4
    assert all("message" in m for m in excerpt["messages"])
