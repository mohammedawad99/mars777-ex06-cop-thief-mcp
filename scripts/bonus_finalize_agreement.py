"""Stage 15E — finalize bonus mutual agreement + Gmail DRAFT preview (never sends).

Loads the Stage 15D canonical bonus_game report, finalizes ``mutual_agreement`` after
partner group orcai-mj's written confirmation (result fields untouched), and writes the
final agreed report, the final partner handoff (with ``result_hash`` + its method), and
a sanitized mutual-agreement evidence file. It then best-effort creates a Gmail **DRAFT**
(never sent) of the JSON-only bonus_game report to the lecturer. It never sends Gmail,
never sets RUN_GMAIL_LIVE, and never prints/writes tokens or student national IDs.

    GOOGLE_OAUTH_CLIENT_SECRETS=... GOOGLE_OAUTH_TOKEN_PATH=... \
    uv run python scripts/bonus_finalize_agreement.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mars777_cop_thief.bonus.bonus_handoff import redact_students, result_hash
from mars777_cop_thief.bonus.finalize import agreement_evidence, final_handoff, finalize_agreement
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
SOURCE = EVID / "bonus_game_report.example.json"
SUBJECT = "MaRs-777 x orcai-mj - Assignment 6 Bonus Game (bonus_game JSON, mutual_agreement)"
NOTES = (
    "Partner group orcai-mj confirmed in writing that the canonical result and official rules "
    "(8x8, origin 0, thief-first, 6 sub-games, max 25 moves, max 5 cop-only barriers, diagonal, "
    "assignment scoring) are identical and correct, and that their agent transcript matched "
    "(Set A: orcai-mj thief survived 25 moves x3; Set B: orcai-mj cop captured at move 14 x3; "
    "totals orcai-mj 90, MaRs-777 30). They explicitly approved mutual_agreement=true. The "
    "result_hash is deterministic over outcome fields only (rules + per-sub-game results + "
    "totals; sorted-keys compact JSON, sha256), excluding timestamps, identities, tokens, and "
    "confirmation status; the partner noted they cannot independently recompute it without our "
    "hash method but confirmed the outcome and transcripts from their agent."
)


def _write(name: str, obj: dict) -> None:
    (EVID / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _draft(report: dict) -> bool:
    """Best-effort: create a Gmail DRAFT (never send) of the JSON body to the lecturer."""
    try:
        from googleapiclient.discovery import build

        from mars777_cop_thief.gmail.auth import load_credentials
        from mars777_cop_thief.gmail.config import load_gmail_config, resolve_paths
        from mars777_cop_thief.gmail.mime_builder import build_raw_message

        config = load_gmail_config()
        creds_path, token_path = resolve_paths(config, os.environ)
        creds = load_credentials(creds_path, token_path, None, run_auth=False)
        service = build("gmail", "v1", credentials=creds)
        raw = build_raw_message(config["recipient"], SUBJECT, report)
        draft = (
            service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
        )
        return bool(draft.get("id"))
    except Exception:
        return False


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    final = finalize_agreement(source, notes=NOTES)
    errors = validate_bonus_game_report(final)
    before, after = result_hash(source), result_hash(final)
    redacted = redact_students(final)
    _write("bonus_game_report_final_agreed.example.json", redacted)
    _write("bonus_game_partner_handoff_final.example.json", final_handoff(final))
    draft_created = _draft(redacted)
    _write(
        "bonus_game_mutual_agreement.example.json",
        agreement_evidence(final, draft_created=draft_created, draft_subject=SUBJECT),
    )
    print(
        json.dumps(
            {
                "mutual_agreement": final["mutual_agreement"],
                "partner_confirmation_status": final["partner_confirmation_status"],
                "bonus_claim": final["bonus_claim"],
                "validation_status": final["validation_status"],
                "validation_errors": errors,
                "result_hash_before": before,
                "result_hash_after": after,
                "result_hash_unchanged": before == after,
                "gmail_draft_created": draft_created,
                "live_gmail_sent": False,
                "bonus_email_sent": False,
            },
            indent=2,
        )
    )
    return 0 if not errors and before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
