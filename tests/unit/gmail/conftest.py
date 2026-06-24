"""Fixtures for the Gmail sender tests: a valid official internal report."""

import json
from pathlib import Path

import pytest

_REPORT_PATH = (
    Path(__file__).resolve().parents[3] / "results" / "evidence" / "local_mcp_report.example.json"
)


@pytest.fixture
def report() -> dict:
    """A validated official internal report (the committed evidence example)."""
    return json.loads(_REPORT_PATH.read_text(encoding="utf-8"))
