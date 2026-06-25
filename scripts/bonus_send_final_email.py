"""Stage 15F — send the final agreed bonus_game report to the lecturer (ONE live email).

Loads results/evidence/bonus_game_report_final_agreed.example.json, runs pre-send checks,
attaches the top-level result_hash to the exact JSON-only payload, and — only with
RUN_GMAIL_LIVE=1 and no prior recorded send — sends exactly one live Gmail message to
Dr. Segal via the existing Gmail infrastructure and external OAuth files. It never sends
internal_game, never sends twice, and never prints/writes OAuth contents, tokens, or
student national IDs. Writes sanitized send evidence (flags + hash + totals only).

    RUN_GMAIL_LIVE=1 \
    GOOGLE_OAUTH_CLIENT_SECRETS=$HOME/private/google-oauth-mars777/credentials.json \
    GOOGLE_OAUTH_TOKEN_PATH=$HOME/private/google-oauth-mars777/token.json \
    uv run python scripts/bonus_send_final_email.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from mars777_cop_thief.bonus.email_payload import (
    EXPECTED_HASH,
    EXPECTED_RECIPIENT,
    payload_is_safe,
    pre_send_checks,
    with_result_hash,
)
from mars777_cop_thief.gmail.auth import load_credentials
from mars777_cop_thief.gmail.config import load_gmail_config, resolve_paths
from mars777_cop_thief.gmail.mime_builder import build_body, build_raw_message
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
SOURCE = EVID / "bonus_game_report_final_agreed.example.json"
SENT_EVID = EVID / "bonus_game_email_sent.example.json"
SUBJECT = "MaRs-777 Assignment 6 - Inter-Group Bonus Game (bonus_game JSON, mutual_agreement)"


def _already_sent() -> bool:
    if not SENT_EVID.is_file():
        return False
    prior = json.loads(SENT_EVID.read_text(encoding="utf-8"))
    return bool(prior.get("live_gmail_sent") and prior.get("gmail_message_id_present"))


def _body_json_ok(payload: dict) -> bool:
    try:
        json.loads(build_body(payload))
        return True
    except (TypeError, ValueError):
        return False


def _send(payload: dict, config: dict) -> str | None:
    creds_path, token_path = resolve_paths(config, os.environ)
    creds = load_credentials(creds_path, token_path, [config["send_scope"]], run_auth=False)
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=creds)
    raw = build_raw_message(config["recipient"], SUBJECT, payload)
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent.get("id")


def _evidence(
    payload: dict, *, sent: bool, msg_id_present: bool, duplicate_prevented: bool
) -> dict:
    totals = payload["totals_by_group"]
    return {
        "stage": "15F",
        "artifact": "bonus_game_email_sent",
        "report_type": "bonus_game",
        "recipient": EXPECTED_RECIPIENT,
        "subject": SUBJECT,
        "live_gmail_sent": sent,
        "bonus_email_sent": sent,
        "internal_game_sent": False,
        "mutual_agreement": True,
        "partner_confirmation_status": "confirmed",
        "partner_hash_confirmation_received": True,
        "result_hash": payload["result_hash"],
        "totals_by_group": {
            "MaRs-777": totals["MaRs-777"]["score"],
            "orcai-mj": totals["orcai-mj"]["score"],
        },
        "sent_at_iso": datetime.now(ZoneInfo("Asia/Jerusalem")).isoformat(),
        "gmail_message_id_present": msg_id_present,
        "duplicate_send_prevented": duplicate_prevented,
        "token_values_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
        "oauth_contents_recorded": False,
    }


def main() -> int:
    config = load_gmail_config()
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    payload = with_result_hash(report)
    checks = pre_send_checks(report)
    ready = (
        all(checks.values())
        and not payload_is_safe(payload)
        and _body_json_ok(payload)
        and config["recipient"] == EXPECTED_RECIPIENT
        and payload["result_hash"] == EXPECTED_HASH
        and not validate_bonus_game_report(payload)
    )
    if not ready:
        print(json.dumps({"ready": False, "checks": checks, "unsafe": payload_is_safe(payload)}))
        return 1
    if _already_sent():  # idempotent: never send a second time
        print(json.dumps({"duplicate_send_prevented": True, "live_gmail_sent": True}))
        return 0
    if os.environ.get(config["run_live_env_var"]) != "1":
        print(json.dumps({"ready": True, "live_gate_off": True, "live_gmail_sent": False}))
        return 0
    message_id = _send(payload, config)
    evidence = _evidence(
        payload, sent=bool(message_id), msg_id_present=bool(message_id), duplicate_prevented=False
    )
    SENT_EVID.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: evidence[k]
                for k in (
                    "live_gmail_sent",
                    "bonus_email_sent",
                    "internal_game_sent",
                    "gmail_message_id_present",
                    "result_hash",
                    "totals_by_group",
                )
            },
            indent=2,
        )
    )
    return 0 if message_id else 1


if __name__ == "__main__":
    raise SystemExit(main())
