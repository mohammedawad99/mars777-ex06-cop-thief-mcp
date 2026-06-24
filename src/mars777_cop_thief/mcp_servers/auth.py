"""Local token auth guard for the MCP servers.

Stage 5 uses an explicit ``auth_token`` argument as **local development auth**,
to be upgraded to request-metadata / OIDC for cloud. The expected token is read
from an environment variable; the real token is never logged or returned.
"""

from __future__ import annotations

import os

REDACTED = "***redacted***"


def expected_token(token_env_var: str) -> str | None:
    """Return the expected token from the environment, or None if unset."""
    return os.environ.get(token_env_var)


def unauthorized(reason: str) -> dict:
    """Structured unauthorized result; never carries the real token."""
    return {"ok": False, "error": "unauthorized", "reason": reason, "auth_token": REDACTED}


def check_auth(provided: str | None, token_env_var: str) -> dict | None:
    """Return None when authorized, else a structured unauthorized result."""
    expected = expected_token(token_env_var)
    if not expected:
        return unauthorized("auth_not_configured")
    if provided != expected:
        return unauthorized("invalid_token")
    return None
