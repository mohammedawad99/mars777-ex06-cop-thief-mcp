"""Result hashing, partner handoff package, and sanitized run evidence (pure).

The ``result_hash`` is a deterministic SHA-256 over the outcome-bearing fields
only (rules + per-sub-game results + totals) — independent of timestamps,
student identities, and confirmation status — so the partner can recompute it
over their own transcript and confirm the canonical result matches. All outputs
here are token-free and redact student national IDs.
"""

from __future__ import annotations

import copy
import hashlib
import json

REDACTED = "REDACTED"
_HASH_SUBGAME_KEYS = (
    "sub_game_index",
    "pairing",
    "cop_group",
    "thief_group",
    "board_size",
    "max_moves",
    "start_positions",
    "final_positions",
    "winner_role",
    "winner_group",
    "move_count",
    "cop_score",
    "thief_score",
    "barriers",
    "outcome_reason",
)


def result_hash(report: dict) -> str:
    """Deterministic SHA-256 of the canonical outcome (excludes time/identity)."""
    core = {
        "official_rules": report["official_rules"],
        "sub_games": [{k: s[k] for k in _HASH_SUBGAME_KEYS} for s in report["sub_games"]],
        "totals_by_group": report["totals_by_group"],
    }
    blob = json.dumps(core, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def redact_students(report: dict) -> dict:
    """Deep-copy the report with every student national ID replaced by ``REDACTED``."""
    safe = copy.deepcopy(report)
    for group in ("group_a", "group_b"):
        for student in safe.get(group, {}).get("students", []):
            if "id" in student:
                student["id"] = REDACTED
    return safe


def partner_handoff(report: dict) -> dict:
    """Token-free, ID-redacted package to send the partner for confirmation."""
    return {
        "handoff_type": "bonus_game_canonical_result",
        "from_group": report["group_a"]["group_code"],
        "for_partner_group": report["group_b"]["group_code"],
        "result_hash": result_hash(report),
        "instructions": (
            "Recompute result_hash over your transcript of this match. If it matches, "
            "reply confirming; mutual_agreement is set only once both results match."
        ),
        "bonus_game": redact_students(report),
        "tokens_recorded": False,
        "student_ids_redacted": True,
    }


def run_evidence(report: dict, *, both_directions: bool, errors) -> dict:
    """Sanitized tracked evidence for the official run (flags + totals; no secrets)."""
    return {
        "stage": "15D",
        "artifact": "bonus_game_official_run",
        "official_bonus_game_run": True,
        "board_size": report["official_rules"]["board_size"],
        "num_sub_games": len(report["sub_games"]),
        "pairing": report["pairing"],
        "both_directions_played": both_directions,
        "sub_game_errors": [e for e in errors if e],
        "totals_by_group": report["totals_by_group"],
        "result_hash": result_hash(report),
        "validation_status": report["validation_status"],
        "bonus_claim": report["bonus_claim"],
        "mutual_agreement": False,
        "partner_confirmation_status": "pending",
        "bonus_email_sent": False,
        "live_gmail_sent": False,
        "token_values_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
    }
