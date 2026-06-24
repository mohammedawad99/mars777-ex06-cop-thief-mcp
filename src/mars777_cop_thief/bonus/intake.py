"""Pure validation/normalization for the inter-group bonus partner intake.

No file or network IO: takes the already-parsed partner dict and returns intake
completeness, partner-URL presence, a sanitized **public-only** info dict (never
tokens — only token *presence* booleans), and human-readable blockers. Used by
``scripts/bonus_partner_readiness.py``.
"""

from __future__ import annotations

REQUIRED_FIELDS = (
    "partner_group_code",
    "partner_group_slug",
    "partner_github_repo",
    "partner_cop_mcp_url",
    "partner_thief_mcp_url",
    "agreement_channel",
)


def is_placeholder(value) -> bool:
    """True when a field is missing/empty or still a ``<placeholder>``."""
    return not isinstance(value, str) or not value.strip() or value.strip().startswith("<")


def normalize_mcp(url: str) -> str:
    """Ensure a partner URL ends with the ``/mcp`` path."""
    url = url.strip().rstrip("/")
    return url if url.endswith("/mcp") else url + "/mcp"


def _kept(data: dict, key: str):
    """Return the value only if it is real (else None) — keeps placeholders out."""
    return None if is_placeholder(data.get(key)) else data.get(key)


def validate_partner(data: dict) -> tuple[bool, bool, dict, list]:
    """Return ``(intake_present, urls_present, public_info, blockers)`` — no tokens."""
    missing = [k for k in REQUIRED_FIELDS if is_placeholder(data.get(k))]
    cop, thief = data.get("partner_cop_mcp_url", ""), data.get("partner_thief_mcp_url", "")
    urls_present = not is_placeholder(cop) and not is_placeholder(thief)
    blockers: list[str] = []
    if urls_present:
        cop, thief = normalize_mcp(cop), normalize_mcp(thief)
        if not (cop.startswith("http") and thief.startswith("http")):
            urls_present = False
            blockers.append("partner URLs are not valid http(s) URLs")
    if missing:
        blockers.append("partner intake incomplete (placeholders): " + ", ".join(missing))
    info = {
        "partner_group_code": _kept(data, "partner_group_code"),
        "partner_github_repo": _kept(data, "partner_github_repo"),
        "partner_cop_mcp_url": cop if urls_present else None,
        "partner_thief_mcp_url": thief if urls_present else None,
        "partner_students_count": len(data.get("partner_students_public") or []),
        "partner_cop_token_present": not is_placeholder(data.get("partner_cop_token")),
        "partner_thief_token_present": not is_placeholder(data.get("partner_thief_token")),
    }
    return (not missing), urls_present, info, blockers
