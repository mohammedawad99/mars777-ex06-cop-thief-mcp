"""Write a small, deterministic, sanitized evidence pack to disk.

Artifacts are normalized (placeholder timestamp, local placeholder URLs), carry
no tokens/secrets, and contain only summaries plus a short transcript excerpt —
never the full event logs. They are safe to commit for README/grading review.
"""

from __future__ import annotations

import json
from pathlib import Path

from mars777_cop_thief.reporting.schemas import (
    GENERATED_AT_PLACEHOLDER,
    LOCAL_COP_URL,
    LOCAL_THIEF_URL,
)
from mars777_cop_thief.reporting.validators import find_token_like

REPORT_FILE = "local_mcp_report.example.json"
SUMMARY_FILE = "local_mcp_summary.example.json"
TRANSCRIPT_FILE = "local_mcp_transcript_excerpt.example.json"


def _sanitize(report: dict) -> dict:
    clean = json.loads(json.dumps(report))  # deep copy
    clean["cop_mcp_url"] = LOCAL_COP_URL
    clean["thief_mcp_url"] = LOCAL_THIEF_URL
    clean["generated_at_iso"] = GENERATED_AT_PLACEHOLDER
    issues = find_token_like(clean)
    if issues:
        raise ValueError(f"evidence not sanitized: {issues}")
    return clean


def _summary(report: dict) -> dict:
    return {
        "report_type": report["report_type"],
        "schema_version": report["schema_version"],
        "group_code": report["group_code"],
        "transport": report["evidence"].get("transport"),
        "mcp_status": report["mcp_status"],
        "cloud_status": report["cloud_status"],
        "email_status": report["email_status"],
        "totals": report["totals"],
        "validation_status": report["validation_status"],
    }


def transcript_excerpt(mcp_report: dict, limit: int = 4) -> dict:
    """A short, coordinate-free excerpt of the first sub-game's messages."""
    sub_games = mcp_report.get("sub_games", [])
    first = sub_games[0] if sub_games else {}
    messages = first.get("transcript", [])[:limit]
    return {
        "sub_game_index": first.get("index"),
        "messages": [
            {
                "turn_index": m["turn_index"],
                "sender": m["sender"],
                "recipient": m["recipient"],
                "message": m["message"],
                "opponent_visible": m["opponent_visible"],
            }
            for m in messages
        ],
        "note": "Excerpt only; full transcripts and event logs are not committed.",
    }


def _write(path: Path, data: dict) -> str:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return str(path)


def write_evidence_pack(directory, official_report: dict, mcp_report: dict) -> dict:
    """Write the three example artifacts; return ``{filename: path}``."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    report = _sanitize(official_report)
    files = {
        REPORT_FILE: report,
        SUMMARY_FILE: _summary(report),
        TRANSCRIPT_FILE: transcript_excerpt(mcp_report),
    }
    return {name: _write(directory / name, data) for name, data in files.items()}
