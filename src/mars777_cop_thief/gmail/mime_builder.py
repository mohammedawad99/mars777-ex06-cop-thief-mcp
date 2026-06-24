"""Build a Gmail MIME message whose body is the JSON report only.

The body is exactly ``json.dumps(report, ensure_ascii=False, indent=2)`` — no
greeting, signature, markdown, or any non-JSON text. The raw message is
base64url-encoded as required by the Gmail API.
"""

from __future__ import annotations

import base64
import json
from email import message_from_bytes, policy
from email.message import EmailMessage


def build_body(report: dict) -> str:
    """The JSON-only email body."""
    return json.dumps(report, ensure_ascii=False, indent=2)


def build_message(recipient: str, subject: str, report: dict) -> EmailMessage:
    """A text/plain message with the JSON body (subject may be human-readable)."""
    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(build_body(report))
    return message


def build_raw_message(recipient: str, subject: str, report: dict) -> str:
    """base64url-encoded raw message for ``messages().send({"raw": ...})``."""
    raw = base64.urlsafe_b64encode(build_message(recipient, subject, report).as_bytes())
    return raw.decode("ascii")


def decode_raw(raw: str) -> EmailMessage:
    """Decode a base64url raw message back into an EmailMessage (for tests)."""
    return message_from_bytes(base64.urlsafe_b64decode(raw.encode("ascii")), policy=policy.default)


def extract_json_body(raw: str) -> dict:
    """Decode the raw message and parse its body back into a dict."""
    return json.loads(decode_raw(raw).get_content())
