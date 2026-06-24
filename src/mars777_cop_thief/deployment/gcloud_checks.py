"""Read-only gcloud / Cloud Run readiness checks (never deploy/build/enable).

Detects whether the ``gcloud`` CLI is installed and, if so, reads version, active
account presence, active project, and (best-effort) billing — all via read-only
commands with a bounded timeout. Missing gcloud, no auth, project mismatch, or
unknown billing are reported as blockers/warnings, never as crashes. No resource
is created and no deploy/build/enable command is ever run. The command runner is
injectable so tests never touch the real CLI or network.
"""

from __future__ import annotations

import os
import shutil
import subprocess

EXPECTED_PROJECT_ID = "api-mars-777"
RECOMMENDED_REGION = "me-west1"
_TIMEOUT = 8


def _run(args: list[str]) -> str | None:
    """Run a bounded read-only command; return stripped stdout or None on failure."""
    try:  # pragma: no cover - exercised only with a real gcloud install
        proc = subprocess.run(args, capture_output=True, text=True, timeout=_TIMEOUT, check=False)
    except (OSError, subprocess.SubprocessError):  # pragma: no cover - env dependent
        return None
    if proc.returncode != 0:  # pragma: no cover - env dependent
        return None
    return proc.stdout.strip()  # pragma: no cover - env dependent


def _intended_region(env) -> tuple[str, str]:
    region = env.get("CLOUD_RUN_REGION")
    if region:
        return region, "env:CLOUD_RUN_REGION"
    return RECOMMENDED_REGION, "recommended_default"


def check_cloud_readiness(
    env=None, *, which=None, runner=None, expected_project=EXPECTED_PROJECT_ID
):
    """Read-only Cloud Run readiness; returns a JSON-serializable dict (no secrets)."""
    env = env if env is not None else os.environ
    which = which or shutil.which
    runner = runner or _run
    region, region_source = _intended_region(env)
    live_deploy_enabled = env.get("RUN_CLOUD_DEPLOY") == "1"
    base = {
        "gcloud_installed": False,
        "authenticated": None,
        "active_account_present": False,
        "active_project": None,
        "expected_project": expected_project,
        "project_matches": None,
        "intended_region": region,
        "region_source": region_source,
        "billing_enabled": None,
        "public_urls_deployed": False,
        "live_deploy_enabled": live_deploy_enabled,
    }

    if which("gcloud") is None:
        return _finish(base, ["gcloud CLI not found on PATH"], [])
    base["gcloud_installed"] = True

    blockers: list[str] = []
    warnings: list[str] = []
    _check_auth(runner, base, blockers)
    _check_project(runner, base, blockers, warnings)
    _check_billing(runner, base, blockers, warnings)
    warnings.append("no public MCP URLs deployed yet (cloud_status: not_deployed)")
    return _finish(base, blockers, warnings)


_ACTIVE_ACCOUNT_CMD = [
    "gcloud",
    "auth",
    "list",
    "--filter=status:ACTIVE",
    "--format=value(account)",
]


def _check_auth(runner, base, blockers) -> None:
    account = runner(_ACTIVE_ACCOUNT_CMD)
    present = bool(account)
    base["authenticated"] = present
    base["active_account_present"] = present
    if not present:
        blockers.append("no active gcloud account (run: gcloud auth login)")


def _check_project(runner, base, blockers, warnings) -> None:
    project = runner(["gcloud", "config", "get-value", "project"]) or None
    base["active_project"] = project
    if project is None:
        warnings.append("active gcloud project unknown; set it to the expected project")
        return
    matches = project == base["expected_project"]
    base["project_matches"] = matches
    if not matches:
        blockers.append(f"active project '{project}' != expected '{base['expected_project']}'")


def _check_billing(runner, base, blockers, warnings) -> None:
    out = runner(
        [
            "gcloud",
            "billing",
            "projects",
            "describe",
            base["expected_project"],
            "--format=value(billingEnabled)",
        ]
    )
    if out is None:
        warnings.append("billing status unknown (read-only check unavailable)")
        return
    enabled = out.strip().lower() == "true"
    base["billing_enabled"] = enabled
    if not enabled:
        blockers.append("billing is disabled for the project (enable before deploy)")


def _finish(base: dict, blockers: list[str], warnings: list[str]) -> dict:
    base["status"] = "ready" if not blockers else "blocked"
    base["blockers"] = blockers
    base["warnings"] = warnings
    return base
