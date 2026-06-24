"""Gmail report senders: dry-run (no API call) and live API sender.

Both validate the report and build a JSON-only MIME message. The dry-run sender
never touches the network. ``SendResult`` is JSON-serializable and carries no
secrets (no token, credential path, or API content).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from mars777_cop_thief.gmail.config import resolve_recipient
from mars777_cop_thief.gmail.mime_builder import build_body, build_raw_message
from mars777_cop_thief.reporting.validators import validate_internal_report


@dataclass
class SendResult:
    """Outcome of a (dry-run or live) Gmail send attempt."""

    status: str
    recipient: str
    subject: str
    body_json_valid: bool
    report_type: str | None
    validation_errors: list = field(default_factory=list)
    gmail_message_id: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "recipient": self.recipient,
            "subject": self.subject,
            "body_json_valid": self.body_json_valid,
            "report_type": self.report_type,
            "validation_errors": self.validation_errors,
            "gmail_message_id": self.gmail_message_id,
            "error_message": self.error_message,
        }


def build_subject(config: dict, report: dict) -> str:
    return config["subject_template"].format(report_type=report.get("report_type", "report"))


def _body_is_json(report: dict) -> bool:
    try:
        json.loads(build_body(report))
        return True
    except (TypeError, ValueError):
        return False


def _prepare(config: dict, report: dict, env):
    recipient = resolve_recipient(config, env)
    subject = build_subject(config, report)
    return recipient, subject, validate_internal_report(report), _body_is_json(report)


class DryRunGmailSender:
    """Validates and builds the message but never calls the Gmail API."""

    def __init__(self, config: dict):
        self.config = config

    def send(self, report: dict, env=None) -> SendResult:
        env = env if env is not None else os.environ
        recipient, subject, errors, body_valid = _prepare(self.config, report, env)
        status = "dry_run" if not errors and body_valid else "failed"
        return SendResult(status, recipient, subject, body_valid, report.get("report_type"), errors)


def _build_gmail_service(creds):  # pragma: no cover - live network/discovery
    from googleapiclient.discovery import build

    return build("gmail", "v1", credentials=creds)


class GmailApiSender:
    """Sends via the Gmail API; the service is injectable for mocking."""

    def __init__(self, config: dict, service_factory=None):
        self.config = config
        self._service_factory = service_factory or _build_gmail_service

    def send(self, report: dict, creds, env=None) -> SendResult:
        env = env if env is not None else os.environ
        recipient, subject, errors, body_valid = _prepare(self.config, report, env)
        if errors or not body_valid:
            return SendResult(
                "failed",
                recipient,
                subject,
                body_valid,
                report.get("report_type"),
                errors,
                error_message="report failed validation",
            )
        raw = build_raw_message(recipient, subject, report)
        service = self._service_factory(creds)
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return SendResult(
            "sent",
            recipient,
            subject,
            body_valid,
            report.get("report_type"),
            gmail_message_id=sent.get("id"),
        )
