"""Finalize the mutually-agreed bonus_game report (pure; no IO, no secrets).

Stage 15E: after partner group orcai-mj confirmed the canonical result in writing,
flip the confirmation/claim flags **without touching any result field** and emit the
final handoff + a mutual-agreement evidence record. The ``result_hash`` is unchanged
because it covers outcome fields only (see ``HASH_METHOD``), so finalizing agreement
does not alter it.
"""

from __future__ import annotations

import copy

from mars777_cop_thief.bonus.bonus_handoff import (
    HASH_ALGORITHM,
    HASH_JSON_SEPARATORS,
    HASH_SUBGAME_FIELDS,
    HASH_TOPLEVEL_FIELDS,
    redact_students,
    result_hash,
)
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

# Self-describing documentation of how result_hash is computed, DERIVED from the actual
# implementation constants in bonus_handoff (kept consistent with the code, not hand-listed),
# so partner group orcai-mj can recompute the digest independently.
HASH_METHOD = {
    "algorithm": HASH_ALGORITHM,
    "encoding": "utf-8",
    "canonical_json": {
        "library": "python json.dumps",
        "sort_keys": True,
        "separators": list(HASH_JSON_SEPARATORS),
        "ensure_ascii": True,
    },
    "included_top_level_fields": list(HASH_TOPLEVEL_FIELDS),
    "included_sub_game_fields": list(HASH_SUBGAME_FIELDS),
    "excluded_fields": [
        "generated_at_iso and all timestamps",
        "student identities / national IDs",
        "tokens",
        "OAuth credential/token contents",
        "Gmail draft metadata (subject, recipient, draft id, draft flags)",
        "mutual_agreement / partner_confirmation_status / bonus_claim",
        "agreement_notes",
        "per-sub-game scores_by_group / transcript_summary / event_count / error",
    ],
    "recompute_recipe": [
        "1. core = {'official_rules': r['official_rules'], 'sub_games': "
        "[{k: s[k] for k in included_sub_game_fields} for s in r['sub_games']], "
        "'totals_by_group': r['totals_by_group']}",
        "2. blob = json.dumps(core, sort_keys=True, separators=(',', ':'))  # ensure_ascii=True",
        "3. result_hash = hashlib.sha256(blob.encode('utf-8')).hexdigest()",
    ],
    "note": "Outcome-only digest: confirmation, identity, timestamp, draft changes never alter it.",
}


def finalize_agreement(report: dict, *, notes: str) -> dict:
    """Return a copy with agreement finalized; winners/moves/totals/rules untouched."""
    final = copy.deepcopy(report)
    final["mutual_agreement"] = True
    final["partner_confirmation_status"] = "confirmed"
    final["bonus_claim"] = True
    final["agreement_notes"] = notes
    final["validation_status"] = "pending"
    final["validation_status"] = "valid" if not validate_bonus_game_report(final) else "invalid"
    return final


def final_handoff(report: dict) -> dict:
    """Token-free, ID-redacted final handoff with the hash and its method, post-confirmation."""
    return {
        "handoff_type": "bonus_game_final_agreed_result",
        "from_group": report["group_a"]["group_code"],
        "for_partner_group": report["group_b"]["group_code"],
        "mutual_agreement": True,
        "partner_confirmation_status": "confirmed",
        "result_hash": result_hash(report),
        "hash_method": HASH_METHOD,
        "instructions": (
            "Partner confirmed the canonical result and official rules in writing and that "
            "their agent transcript matched; mutual_agreement is now final."
        ),
        "bonus_game": redact_students(report),
        "tokens_recorded": False,
        "student_ids_redacted": True,
    }


def agreement_evidence(report: dict, *, draft_created: bool, draft_subject: str) -> dict:
    """Sanitized tracked mutual-agreement + Gmail-draft evidence (flags only; no secrets)."""
    return {
        "stage": "15E",
        "artifact": "bonus_game_mutual_agreement",
        "official_bonus_game_run": True,
        "partner_confirmation_received": True,
        "mutual_agreement": True,
        "partner_confirmation_status": "confirmed",
        "bonus_claim": True,
        "board_size": report["official_rules"]["board_size"],
        "num_sub_games": len(report["sub_games"]),
        "totals_by_group": report["totals_by_group"],
        "result_hash": result_hash(report),
        "hash_method": HASH_METHOD,
        "validation_status": report["validation_status"],
        "gmail_draft_created": draft_created,
        "draft_subject": draft_subject,
        "draft_recipient_category": "lecturer",
        "bonus_email_sent": False,
        "live_gmail_sent": False,
        "token_values_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
    }
