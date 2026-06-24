"""Combined live-readiness preflight (no live send, no deploy, read-only).

Bridges local implementation to live operations by combining the Gmail OAuth
external-file preflight, the read-only Cloud Run readiness checks, and the
existing packaging preflight into one JSON report. It makes blockers explicit and
exits 0 whenever the checks themselves complete — blockers do not fail the run.
It never triggers a live Gmail send, a live Gemini call, or any cloud deployment.

    uv run python -m mars777_cop_thief.deployment.live_readiness
"""

from __future__ import annotations

import json
import os

from mars777_cop_thief.deployment.gcloud_checks import check_cloud_readiness
from mars777_cop_thief.deployment.preflight import run_preflight
from mars777_cop_thief.gmail.preflight import run_gmail_preflight


def _manual_actions(gmail: dict, cloud: dict) -> list[str]:
    actions: list[str] = []
    if gmail["status"] != "ready":
        actions.append("place valid OAuth files outside the repo and point the env vars at them")
    if not cloud["gcloud_installed"]:
        actions.append("install the gcloud CLI")
    if cloud.get("authenticated") is False:
        actions.append("authenticate: gcloud auth login")
    if cloud.get("project_matches") is not True:
        actions.append(f"select project {cloud['expected_project']}")
    if cloud.get("billing_enabled") is not True:
        actions.append("enable billing for the project (read-only check could not confirm it)")
    actions.append(f"choose/confirm Cloud Run region (intended: {cloud['intended_region']})")
    actions.append("deploy the two MCP services and record their public URLs (manual, gated)")
    actions.append("for a live report, run send_report with RUN_GMAIL_LIVE=1 (OAuth files present)")
    return actions


def run_live_readiness(env=None, *, root=None, which=None, runner=None) -> dict:
    """Combine Gmail, cloud, and packaging readiness into one JSON-safe report."""
    env = env if env is not None else os.environ
    gmail = run_gmail_preflight(env=env, root=root)
    cloud = check_cloud_readiness(env=env, which=which, runner=runner)
    packaging = run_preflight(root=root)
    blockers = list(gmail["blockers"]) + list(cloud["blockers"])
    if not packaging["passed"]:
        blockers.append("cloud packaging preflight is not passing")
    return {
        "status": "ok",
        "ready_for_live": not blockers,
        "gmail_readiness": gmail,
        "cloud_readiness": cloud,
        "packaging_preflight": {"status": packaging["status"], "passed": packaging["passed"]},
        "blockers": blockers,
        "remaining_manual_actions": _manual_actions(gmail, cloud),
        "live_send_attempted": False,
        "cloud_deploy_attempted": False,
    }


def main(env=None) -> int:
    result = run_live_readiness(env=env)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1  # pragma: no cover - status is always ok


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
