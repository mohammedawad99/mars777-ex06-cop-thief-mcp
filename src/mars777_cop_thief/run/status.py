"""Structured failure classification and secret-safe redaction.

Maps exceptions to a fixed set of categories and redacts known dummy tokens from
messages, so a run status can be recorded and surfaced without leaking secrets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from mars777_cop_thief.gmail.auth import GmailAuthError
from mars777_cop_thief.gmail.config import GmailConfigError
from mars777_cop_thief.llm.config import LlmConfigError
from mars777_cop_thief.reporting.schemas import DUMMY_TOKEN_HINTS
from mars777_cop_thief.shared.config import ConfigError


class FailureCategory(StrEnum):
    """Stable failure categories for run auditing."""

    CONFIG_ERROR = "config_error"
    AUTH_ERROR = "auth_error"
    MCP_TRANSPORT_ERROR = "mcp_transport_error"
    MCP_TOOL_ERROR = "mcp_tool_error"
    LLM_PARSE_ERROR = "llm_parse_error"
    ILLEGAL_ACTION = "illegal_action"
    REPORT_VALIDATION_ERROR = "report_validation_error"
    GMAIL_AUTH_ERROR = "gmail_auth_error"
    GMAIL_SEND_ERROR = "gmail_send_error"
    SECRET_RISK = "secret_risk"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


_BY_TYPE = (
    (TimeoutError, FailureCategory.TIMEOUT),
    (GmailAuthError, FailureCategory.GMAIL_AUTH_ERROR),
    (GmailConfigError, FailureCategory.CONFIG_ERROR),
    (LlmConfigError, FailureCategory.CONFIG_ERROR),
    (ConfigError, FailureCategory.CONFIG_ERROR),
)

_BY_NAME = (
    ("timeout", FailureCategory.TIMEOUT),
    ("auth", FailureCategory.AUTH_ERROR),
    ("config", FailureCategory.CONFIG_ERROR),
    ("transport", FailureCategory.MCP_TRANSPORT_ERROR),
    ("connect", FailureCategory.MCP_TRANSPORT_ERROR),
)


def classify_exception(exc: BaseException) -> FailureCategory:
    """Classify an exception without inspecting its (possibly sensitive) message."""
    for exc_type, category in _BY_TYPE:
        if isinstance(exc, exc_type):
            return category
    name = type(exc).__name__.lower()
    for fragment, category in _BY_NAME:
        if fragment in name:
            return category
    return FailureCategory.UNKNOWN


def redact(message: str) -> str:
    """Replace any known dummy token in a message with ``[REDACTED]``."""
    safe = message
    for hint in DUMMY_TOKEN_HINTS:
        safe = safe.replace(hint, "[REDACTED]")
    return safe


@dataclass(frozen=True)
class RunStatus:
    """Outcome of a run step, with a redacted message on failure."""

    ok: bool
    category: str | None = None
    message: str | None = None

    @classmethod
    def failed(cls, exc: BaseException) -> RunStatus:
        return cls(False, classify_exception(exc).value, redact(str(exc)))

    def to_dict(self) -> dict:
        return {"ok": self.ok, "category": self.category, "message": self.message}
