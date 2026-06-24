"""Create a Gmail DRAFT preview of the official Assignment 6 report (never sends).

Rebuilds the official internal report from the sanitized tracked evidence by
restoring the real student identities from the local git-ignored file
(``MARS777_STUDENTS_FILE``), validates it, and creates a Gmail **draft** addressed
to the authenticated account **itself** (NOT the lecturer). It never sends, never
sets a live flag, and never prints the JSON body, student IDs, recipient address,
token, or any secret — only safe boolean/count flags.

    GOOGLE_OAUTH_CLIENT_SECRETS=$HOME/private/google-oauth-mars777/credentials.json \
    GOOGLE_OAUTH_TOKEN_PATH=$HOME/private/google-oauth-mars777/token.json \
    MARS777_STUDENTS_FILE=.secrets/students.local.json \
    uv run python scripts/gmail_draft_preview.py
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from mars777_cop_thief.gmail.auth import load_credentials
from mars777_cop_thief.gmail.config import load_gmail_config, resolve_paths
from mars777_cop_thief.gmail.mime_builder import build_body, build_raw_message
from mars777_cop_thief.reporting.validators import validate_internal_report

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
TRACKED_REPORT = EVID / "public_cloud_full_game.example.json"
STUDENTS_FILE = Path(
    os.environ.get("MARS777_STUDENTS_FILE", _ROOT / ".secrets" / "students.local.json")
)
SUBJECT = "PREVIEW ONLY - MaRs-777 Assignment 6 JSON Report"


def _official_report() -> dict:
    """Rebuild the real official report: sanitized evidence + real local students."""
    report = json.loads(TRACKED_REPORT.read_text(encoding="utf-8"))
    report.pop("identity_privacy", None)  # evidence-only block, not part of the schema
    report["students"] = json.loads(STUDENTS_FILE.read_text(encoding="utf-8"))["students"]
    report["generated_at_iso"] = datetime.now(UTC).isoformat()
    return report


def _body_json_valid(report: dict) -> bool:
    try:
        json.loads(build_body(report))
        return True
    except (TypeError, ValueError):
        return False


def _placeholders_remaining(report: dict) -> bool:
    blob = json.dumps(report, ensure_ascii=False)
    return "REPLACE_WITH" in blob or "EXAMPLE_GENERATED" in blob


def _create_draft(report: dict) -> tuple[str | None, bool]:
    """Load OAuth creds, resolve the self address, create a Gmail draft (never send)."""
    config = load_gmail_config()
    creds_path, token_path = resolve_paths(config, os.environ)
    # scopes=None → use the token's own granted scopes (which include draft/compose
    # from the prior manual OAuth smoke); a draft needs compose/modify, not just send.
    creds = load_credentials(creds_path, token_path, None, run_auth=False)
    from googleapiclient.discovery import build  # live-only import

    service = build("gmail", "v1", credentials=creds)
    self_email = service.users().getProfile(userId="me").execute()["emailAddress"]
    raw = build_raw_message(self_email, SUBJECT, report)
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft.get("id"), self_email == config["recipient"]


def _write_evidence(created: bool, body_valid: bool, schema_valid: bool, lecturer: bool, n: int):
    evid = {
        "stage": "14C",
        "artifact": "gmail_draft_preview",
        "draft_created": created,
        "draft_subject": SUBJECT,
        "body_json_valid": body_valid,
        "report_schema_valid": schema_valid,
        "live_gmail_sent": False,
        "lecturer_recipient_used": lecturer,
        "recipient_category": "authenticated_self_account",
        "identity_source": "local_ignored_file",
        "ids_redacted_in_tracked_evidence": True,
        "token_values_recorded": False,
        "students_count": n,
    }
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "gmail_draft_preview.example.json").write_text(
        json.dumps(evid, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    report = _official_report()
    schema_valid = not validate_internal_report(report)
    body_valid = _body_json_valid(report)
    placeholders = _placeholders_remaining(report)
    n = len(report["students"])
    created, lecturer = False, False
    if schema_valid and body_valid and not placeholders:
        draft_id, lecturer = _create_draft(report)
        created = bool(draft_id)
    _write_evidence(created, body_valid, schema_valid, lecturer, n)
    print(
        json.dumps(
            {
                "draft_created": created,
                "body_json_valid": body_valid,
                "report_schema_valid": schema_valid,
                "placeholders_remaining": placeholders,
                "students_count": n,
                "recipient_is_lecturer": lecturer,
                "live_gmail_sent": False,
            },
            indent=2,
        )
    )
    return 0 if created else 1


if __name__ == "__main__":
    raise SystemExit(main())
