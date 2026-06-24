"""Gmail JSON report sender (dry-run by default; live sending is opt-in).

The email body is the JSON report only. OAuth credential/token files live outside
the repo; no secret is committed, logged, or returned. Live sending requires
``RUN_GMAIL_LIVE=1`` and is never performed during tests.
"""

from mars777_cop_thief.gmail.config import GmailConfigError, load_gmail_config
from mars777_cop_thief.gmail.mime_builder import (
    build_raw_message,
    extract_json_body,
)
from mars777_cop_thief.gmail.sender import DryRunGmailSender, GmailApiSender, SendResult

__all__ = [
    "DryRunGmailSender",
    "GmailApiSender",
    "GmailConfigError",
    "SendResult",
    "build_raw_message",
    "extract_json_body",
    "load_gmail_config",
]
