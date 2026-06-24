"""Gmail report sender CLI (dry-run by default; live-gated).

Run with:

    uv run python -m mars777_cop_thief.gmail.send_report

Dry-run unless ``RUN_GMAIL_LIVE=1``. When live but credentials/token are missing
it returns a controlled failure (exit non-zero). Prints a JSON result only and
never prints credentials, token, or any secret.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mars777_cop_thief.gmail.auth import GmailAuthError, load_credentials
from mars777_cop_thief.gmail.config import load_gmail_config, resolve_paths, resolve_recipient
from mars777_cop_thief.gmail.sender import (
    DryRunGmailSender,
    GmailApiSender,
    SendResult,
    build_subject,
)
from mars777_cop_thief.shared.config import load_json_config

_ROOT = Path(__file__).resolve().parents[3]
_REPORT_PATH = _ROOT / "results" / "evidence" / "local_mcp_report.example.json"


def _default_report() -> dict:
    """Load the committed official internal report (evidence example)."""
    return load_json_config(_REPORT_PATH)


def _auth_failed(config: dict, report: dict, env, message: str) -> dict:
    return SendResult(
        "failed",
        resolve_recipient(config, env),
        build_subject(config, report),
        True,
        report.get("report_type"),
        error_message=message,
    ).to_dict()


def run_send(env=None, report=None) -> dict:
    """Dry-run unless live; on live, authenticate then send (or fail safely)."""
    env = env if env is not None else os.environ
    config = load_gmail_config()
    report = report if report is not None else _default_report()
    if env.get(config["run_live_env_var"]) != "1":
        return DryRunGmailSender(config).send(report, env).to_dict()
    creds_path, token_path = resolve_paths(config, env)
    run_auth = env.get(config["run_auth_env_var"]) == "1"
    try:
        creds = load_credentials(creds_path, token_path, [config["send_scope"]], run_auth=run_auth)
    except GmailAuthError as exc:
        return _auth_failed(config, report, env, str(exc))
    return GmailApiSender(config).send(report, creds, env).to_dict()  # pragma: no cover - live send


def main() -> int:
    result = run_send()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"dry_run", "skipped", "sent"} else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
