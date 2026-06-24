"""Aggregate validation of a full official report (with optional manifest check).

Checks the run as a whole: exactly ``num_sub_games`` decided, totals equal to the
sum of sub-game scores, no invalid sub-games, required status fields present, no
token-like content, and local URLs only when ``cloud_status`` is local.
"""

from __future__ import annotations

from mars777_cop_thief.reporting.schemas import LOCAL_CLOUD_STATUSES
from mars777_cop_thief.reporting.validators import find_token_like

_STATUS_FIELDS = ("mcp_status", "cloud_status", "email_status", "validation_status")


def _url_locality(report: dict) -> list[str]:
    cloud = report.get("cloud_status")
    if cloud in LOCAL_CLOUD_STATUSES:
        return []
    urls = [report.get("cop_mcp_url", ""), report.get("thief_mcp_url", "")]
    return [f"local URL not allowed when cloud_status={cloud}" for u in urls if "127.0.0.1" in u]


def validate_full_report(report: dict, manifest: dict | None = None) -> list[str]:
    """Return aggregate validation errors for a full official report."""
    errors: list[str] = []
    sub_games = report.get("sub_games", [])
    expected = report.get("config_summary", {}).get("num_sub_games")
    if expected is not None and len(sub_games) != expected:
        errors.append(f"expected {expected} sub-games, got {len(sub_games)}")
    totals = report.get("totals", {})
    if totals.get("cop_score") != sum(s.get("cop_score", 0) for s in sub_games):
        errors.append("cop totals mismatch")
    if totals.get("thief_score") != sum(s.get("thief_score", 0) for s in sub_games):
        errors.append("thief totals mismatch")
    if totals.get("invalid_sub_games"):
        errors.append("invalid sub-games present")
    for index, sub_game in enumerate(sub_games):
        if sub_game.get("winner") not in {"cop", "thief"}:
            errors.append(f"sub_game[{index}] missing winner")
        if not sub_game.get("outcome_reason"):
            errors.append(f"sub_game[{index}] missing outcome_reason")
    errors += [f"missing status field: {f}" for f in _STATUS_FIELDS if f not in report]
    errors += find_token_like(report)
    errors += _url_locality(report)
    if manifest is not None:
        identity = manifest.get("run_identity", {})
        if identity.get("cloud_status") != report.get("cloud_status"):
            errors.append("manifest cloud_status does not match report")
    return errors
