"""Full public-cloud MCP game + official report dry-run (no live Gmail; no tokens printed).

Plays the full default game (6 sub-games) over the deployed public Cloud Run MCP
URLs, builds and validates the official internal report (with the real public
`/mcp` URLs and repo), runs the Gmail sender in DRY-RUN only, and writes
sanitized, token-free evidence. Tokens are read from the environment (sourced from
the local git-ignored `.secrets/`) and are never printed or written anywhere.

Student identities (national IDs + EN/HE names) are loaded at runtime from a local
git-ignored file (``MARS777_STUDENTS_FILE``, default ``.secrets/students.local.json``)
so the real IDs reach the in-memory official report and the Gmail dry-run **only**.
The tracked evidence redacts the national IDs (``id`` → ``REDACTED``) and records
privacy flags; no national-ID value is ever written to a tracked file.

    set -a; . .secrets/cloud-run.local.env; set +a
    uv run python scripts/public_cloud_final_dry_run.py
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
from pathlib import Path

from fastmcp import Client

from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.gmail.send_report import run_send
from mars777_cop_thief.mcp_client.client import wait_ready
from mars777_cop_thief.mcp_client.game_flow import run_mcp_full_game
from mars777_cop_thief.mcp_client.game_report import build_mcp_report
from mars777_cop_thief.reporting.official_report import build_official_internal_report
from mars777_cop_thief.reporting.schemas import GENERATED_AT_PLACEHOLDER
from mars777_cop_thief.reporting.validators import validate_internal_report
from mars777_cop_thief.shared.config import load_game_config

_ROOT = Path(__file__).resolve().parents[1]
GAME_CONFIG_PATH = _ROOT / "config" / "game.default.json"
EVID = _ROOT / "results" / "evidence"
COP_URL = os.environ.get("COP_MCP_URL", "https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app/mcp")
THIEF_URL = os.environ.get("THIEF_MCP_URL", "https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app/mcp")
REPO = "https://github.com/mohammedawad99/mars777-ex06-cop-thief-mcp"
STUDENTS_FILE = Path(
    os.environ.get("MARS777_STUDENTS_FILE", _ROOT / ".secrets" / "students.local.json")
)


def _load_students() -> list[dict]:
    """Load real student identities from a local git-ignored file (never tracked)."""
    if not STUDENTS_FILE.is_file():
        raise SystemExit(
            f"students file missing; set MARS777_STUDENTS_FILE (looked for {STUDENTS_FILE})"
        )
    return json.loads(STUDENTS_FILE.read_text(encoding="utf-8"))["students"]


def _redact_students(report: dict) -> dict:
    """Deep-copy the report with national-IDs redacted and privacy flags added."""
    red = copy.deepcopy(report)
    students = red.get("students", [])
    for student in students:
        if "id" in student:
            student["id"] = "REDACTED"
    red["identity_privacy"] = {
        "students_count": len(students),
        "ids_required_for_official_report": True,
        "ids_loaded_from_local_ignored_file": True,
        "ids_redacted_in_tracked_evidence": True,
    }
    return red


def _cloud_official_report(config: dict, results, students: list[dict]) -> dict:
    mcp = build_mcp_report(config, results, COP_URL, THIEF_URL)
    mcp.update(
        {
            "github_repo": REPO,
            "transport": "public_cloud_https",
            "mcp_status": "cloud_verified",
            "cloud_status": "deployed",
            "email_status": "dry_run",
        }
    )
    return build_official_internal_report(
        mcp, students=students, generated_at_iso=GENERATED_AT_PLACEHOLDER
    )


async def _play(config: dict, cop_token: str, thief_token: str):
    if not (await wait_ready(COP_URL) and await wait_ready(THIEF_URL)):
        raise SystemExit("public MCP servers not ready")
    engine = GameEngine(config)
    async with Client(COP_URL) as cop, Client(THIEF_URL) as thief:
        results = await run_mcp_full_game(
            engine, config["num_sub_games"], cop, thief, cop_token, thief_token
        )
        thief_tools = sorted(t.name for t in await thief.list_tools())
        denied = (
            await cop.call_tool(
                "get_observation", {"cop": [0, 0], "thief": [1, 1], "auth_token": "wrong-token"}
            )
        ).data
    return results, thief_tools, denied


def _evidence(report: dict, dry: dict, thief_tools, denied) -> dict:
    return {
        "stage": "14B",
        "project_id": "api-mars-777",
        "region": "me-west1",
        "cop_mcp_url": COP_URL,
        "thief_mcp_url": THIEF_URL,
        "num_sub_games": len(report["sub_games"]),
        "max_moves": report["config_summary"]["max_moves"],
        "totals": report["totals"],
        "report_schema_valid": report["validation_status"] == "valid",
        "all_sub_games_decided": all(s["winner"] in ("cop", "thief") for s in report["sub_games"]),
        "auth_negative_rejected": denied.get("error") == "unauthorized",
        "thief_no_barrier_tool": "place_barrier_candidate" not in thief_tools,
        "gmail_dry_run_status": dry["status"],
        "gmail_body_json_valid": dry["body_json_valid"],
        "live_gmail_sent": False,
        "intergroup_bonus_run": False,
        "token_values_recorded": False,
        "students_count": len(report["students"]),
        "ids_required_for_official_report": True,
        "ids_loaded_from_local_ignored_file": True,
        "ids_redacted_in_tracked_evidence": True,
    }


def main() -> int:
    config = load_game_config(GAME_CONFIG_PATH)
    students = _load_students()  # real IDs stay in memory only
    cop_token = os.environ["COP_MCP_TOKEN"]
    thief_token = os.environ["THIEF_MCP_TOKEN"]
    results, thief_tools, denied = asyncio.run(_play(config, cop_token, thief_token))
    report = _cloud_official_report(config, results, students)
    errors = validate_internal_report(report)
    dry = run_send(env={"RUN_GMAIL_LIVE": "0"}, report=report)  # real report in-memory; never live
    evid = _evidence(report, dry, thief_tools, denied)
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "public_cloud_full_game.example.json").write_text(
        json.dumps(_redact_students(report), indent=2) + "\n", encoding="utf-8"
    )
    (EVID / "final_report_dry_run.example.json").write_text(
        json.dumps(evid, indent=2) + "\n", encoding="utf-8"
    )
    passed = (
        not errors
        and evid["report_schema_valid"]
        and evid["all_sub_games_decided"]
        and evid["auth_negative_rejected"]
        and dry["status"] == "dry_run"
        and len(report["sub_games"]) == config["num_sub_games"]
    )
    print(json.dumps({**evid, "validation_errors": errors, "passed": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
