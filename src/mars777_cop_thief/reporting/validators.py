"""Validation and token-safety checks for the official reports.

Validators return a list of human-readable error strings (empty == valid); they
never raise on a structurally invalid report. The token scan walks the whole
structure so no auth/secret material can hide in a nested key or value.
"""

from __future__ import annotations

from mars777_cop_thief.reporting.schemas import (
    BONUS_GAME_REQUIRED_SUBGAME,
    BONUS_GAME_REQUIRED_TOP,
    BONUS_REPORT_TYPE,
    BONUS_REQUIRED_TOP,
    DUMMY_TOKEN_HINTS,
    FORBIDDEN_PATTERNS,
    INTERNAL_REPORT_TYPE,
    INTERNAL_REQUIRED_SUBGAME,
    INTERNAL_REQUIRED_TOP,
    INTERNAL_REQUIRED_TOTALS,
    LOCAL_CLOUD_STATUSES,
)


def find_token_like(obj, path: str = "report") -> list[str]:
    """Return paths where a forbidden token/secret pattern appears."""
    issues: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if any(pattern in str(key).lower() for pattern in FORBIDDEN_PATTERNS):
                issues.append(f"forbidden key at {path}.{key}")
            issues.extend(find_token_like(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            issues.extend(find_token_like(value, f"{path}[{index}]"))
    elif isinstance(obj, str):
        low = obj.lower()
        if any(p in low for p in FORBIDDEN_PATTERNS + DUMMY_TOKEN_HINTS):
            issues.append(f"forbidden value at {path}")
    return issues


def _url_locality_errors(report: dict) -> list[str]:
    cloud = report.get("cloud_status")
    if cloud in LOCAL_CLOUD_STATUSES:
        return []
    urls = [report.get("cop_mcp_url", ""), report.get("thief_mcp_url", "")]
    local = [u for u in urls if "127.0.0.1" in u or "localhost" in u]
    return [f"local URL not allowed when cloud_status={cloud}: {u}" for u in local]


def validate_internal_report(report: dict) -> list[str]:
    """Return validation errors for an internal report (empty == valid)."""
    errors: list[str] = []
    if report.get("report_type") != INTERNAL_REPORT_TYPE:
        errors.append("report_type must be internal_game")
    errors += [f"missing top field: {k}" for k in INTERNAL_REQUIRED_TOP if k not in report]
    for index, sub_game in enumerate(report.get("sub_games", [])):
        errors += [
            f"sub_game[{index}] missing: {k}"
            for k in INTERNAL_REQUIRED_SUBGAME
            if k not in sub_game
        ]
    totals = report.get("totals", {})
    errors += [f"totals missing: {k}" for k in INTERNAL_REQUIRED_TOTALS if k not in totals]
    errors += find_token_like(report)
    errors += _url_locality_errors(report)
    return errors


def is_valid_internal_report(report: dict) -> bool:
    """True when the internal report has no validation errors."""
    return not validate_internal_report(report)


def validate_bonus_report(report: dict) -> list[str]:
    """Return validation errors for a bonus report (empty == valid)."""
    errors: list[str] = []
    if report.get("report_type") != BONUS_REPORT_TYPE:
        errors.append("report_type must be bonus_game")
    errors += [f"missing top field: {k}" for k in BONUS_REQUIRED_TOP if k not in report]
    errors += find_token_like(report)
    return errors


def validate_bonus_game_report(report: dict) -> list[str]:
    """Return validation errors for a played bonus_game report (empty == valid)."""
    errors: list[str] = []
    if report.get("report_type") != BONUS_REPORT_TYPE:
        errors.append("report_type must be bonus_game")
    errors += [f"missing top field: {k}" for k in BONUS_GAME_REQUIRED_TOP if k not in report]
    for index, sub_game in enumerate(report.get("sub_games", [])):
        errors += [
            f"sub_game[{index}] missing: {k}"
            for k in BONUS_GAME_REQUIRED_SUBGAME
            if k not in sub_game
        ]
    if report.get("mutual_agreement") is True and report.get("partner_confirmation_status") != (
        "confirmed"
    ):
        errors.append(
            "mutual_agreement must stay false until partner_confirmation_status=confirmed"
        )
    errors += find_token_like(report)
    return errors
