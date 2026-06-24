"""Generate the local MCP-backed evidence pack.

Run with:

    uv run python -m mars777_cop_thief.reporting.generate_evidence_pack

Plays a local MCP-backed game over HTTP (via the Stage 7 smoke), builds the
official internal report, validates it, and writes sanitized example artifacts
under ``results/evidence/``. No email is sent and nothing is deployed.
"""

from __future__ import annotations

import json
from pathlib import Path

from mars777_cop_thief.mcp_client.game_smoke import run_game_smoke
from mars777_cop_thief.reporting.evidence import write_evidence_pack
from mars777_cop_thief.reporting.official_report import build_official_internal_report
from mars777_cop_thief.reporting.schemas import LOCAL_COP_URL, LOCAL_THIEF_URL
from mars777_cop_thief.reporting.validators import validate_internal_report

_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EVIDENCE_DIR = _ROOT / "results" / "evidence"


def generate(directory=None, mcp_report: dict | None = None) -> dict:
    """Build, validate, and write the evidence pack; return a status dict."""
    if mcp_report is None:
        mcp_report = run_game_smoke()
    mcp_report["cop_mcp_url"] = LOCAL_COP_URL
    mcp_report["thief_mcp_url"] = LOCAL_THIEF_URL
    official = build_official_internal_report(mcp_report)
    errors = validate_internal_report(official)
    files = write_evidence_pack(directory or DEFAULT_EVIDENCE_DIR, official, mcp_report)
    return {
        "validation_status": official["validation_status"],
        "validation_errors": errors,
        "files": files,
    }


def main() -> int:
    result = generate()
    print(json.dumps(result, indent=2))
    return 0 if result["validation_status"] == "valid" and not result["validation_errors"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
