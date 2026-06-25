"""Pure pre-send checks + email payload shaping for the final bonus_game email.

No IO and no network: validates the agreed bonus_game report, attaches the
top-level ``result_hash`` to the exact JSON that will be emailed, and scans the
payload for anything that must never leave the machine (tokens, national IDs,
``.secrets`` paths). Used by ``scripts/bonus_send_final_email.py``.
"""

from __future__ import annotations

import copy
import json
import re

from mars777_cop_thief.bonus.bonus_handoff import result_hash
from mars777_cop_thief.reporting.validators import find_token_like

EXPECTED_RECIPIENT = "rmisegal+uoh26b@gmail.com"
EXPECTED_HASH = "a0fdf72d1122280c3637d54f0bda5656c6c6c2b257220347d9675b405972ac68"
_NINE_DIGITS = re.compile(r"\b\d{9}\b")


def pre_send_checks(report: dict) -> dict:
    """Boolean gate checks for the agreed bonus_game report (all must be True to send)."""
    totals = report.get("totals_by_group") or {}
    return {
        "report_type_bonus_game": report.get("report_type") == "bonus_game",
        "mutual_agreement_true": report.get("mutual_agreement") is True,
        "partner_confirmed": report.get("partner_confirmation_status") == "confirmed",
        "validation_valid": report.get("validation_status") == "valid",
        "mars777_total_30": (totals.get("MaRs-777") or {}).get("score") == 30,
        "orcai_total_90": (totals.get("orcai-mj") or {}).get("score") == 90,
        "six_sub_games": len(report.get("sub_games") or []) == 6,
        "board_8x8": (report.get("official_rules") or {}).get("board_size") == [8, 8],
    }


def with_result_hash(report: dict) -> dict:
    """Return a copy of the report with the top-level ``result_hash`` attached.

    Only adds the hash field; winners, rules, totals, sub_games, and agreement
    flags are untouched, so the digest of the outcome core is unchanged.
    """
    payload = copy.deepcopy(report)
    payload["result_hash"] = result_hash(report)
    return payload


def payload_is_safe(payload: dict) -> list[str]:
    """Return reasons the payload is unsafe to email (empty == safe)."""
    blob = json.dumps(payload, ensure_ascii=False)
    issues: list[str] = []
    if find_token_like(payload):
        issues.append("token-like key/value present")
    if _NINE_DIGITS.search(blob):
        issues.append("9-digit national-ID-like value present")
    if ".secrets" in blob:
        issues.append("local .secrets path present")
    return issues
