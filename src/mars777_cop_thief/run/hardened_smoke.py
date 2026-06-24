"""Hardened local smoke: run, aggregate-validate, build a manifest, and gate it.

Reuses the fake-local prompted MCP full-game output, builds the official report,
validates it as a whole, builds a run manifest, and runs the programmatic quality
checks. Prints a structured JSON summary; writes no secrets and no raw logs.
"""

from __future__ import annotations

import json

from mars777_cop_thief.gmail.config import load_gmail_config
from mars777_cop_thief.gmail.sender import DryRunGmailSender
from mars777_cop_thief.mcp_client.prompted_game_smoke import run_prompted_game_smoke
from mars777_cop_thief.reporting.official_report import build_official_internal_report
from mars777_cop_thief.reporting.validators import find_token_like
from mars777_cop_thief.run.identity import build_run_identity
from mars777_cop_thief.run.manifest import build_manifest, scan_manifest_secrets
from mars777_cop_thief.run.validation import validate_full_report

_GATES = {
    "aggregate_report_validation": "run",
    "token_scan": "run",
    "json_serialization": "run",
    "gmail_dry_run": "run",
}


def _json_ok(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


def _checks(
    prompted: dict, official: dict, manifest: dict, errors: list, gmail_valid: bool
) -> dict:
    return {
        "report_valid": not errors,
        "totals_valid": not any("totals" in error for error in errors),
        "no_secret_like_content": not find_token_like(official)
        and not scan_manifest_secrets(manifest),
        "json_serializable": _json_ok(official) and _json_ok(manifest),
        "local_mcp_verified": bool(prompted.get("passed"))
        and bool(prompted.get("hidden_state_respected")),
        "gmail_body_json_only": gmail_valid,
    }


def run_hardened_smoke(
    num_sub_games: int | None = None,
    env=None,
    prompted_report: dict | None = None,
    created_at_utc: str | None = None,
    git_commit: str | None = "__auto__",
) -> dict:
    """Build and gate a hardened run summary (servers run only without an injected report)."""
    env = env if env is not None else {}
    prompted = prompted_report
    if prompted is None:  # pragma: no cover - live HTTP path (exercised by the CLI)
        prompted = run_prompted_game_smoke(num_sub_games=num_sub_games)
    official = build_official_internal_report(prompted)
    errors = validate_full_report(official)
    identity = build_run_identity(
        prompted["config"],
        stage="hardened",
        mode=prompted.get("mode", "mcp-backed-prompted"),
        seed=0,
        created_at_utc=created_at_utc,
        git_commit=git_commit,
        cloud_status=official["cloud_status"],
    )
    manifest = build_manifest(identity, official["config_summary"], validation_gates=_GATES)
    gmail = DryRunGmailSender(load_gmail_config()).send(official, env).to_dict()
    checks = _checks(prompted, official, manifest, errors, gmail["body_json_valid"])
    passed = all(checks.values())
    return {
        "status": "ok" if passed else "failed",
        "passed": passed,
        "run_id": identity.run_id,
        "checks": checks,
        "report_validation_errors": errors,
        "totals": official["totals"],
        "manifest": manifest,
    }


def main() -> int:
    summary = run_hardened_smoke()
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
