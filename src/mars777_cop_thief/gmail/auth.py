"""Gmail OAuth credential loading (lazy; never logs secret content).

Loads a token from a path outside the repo, refreshes it when expired, and runs
a local desktop OAuth flow only when ``RUN_GMAIL_AUTH=1``. All filesystem and
Google-library access is injected via ``_AuthDeps`` so tests exercise every
branch without real files or network.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass


class GmailAuthError(RuntimeError):
    """Raised when credentials/token cannot be loaded (no secret content)."""


@dataclass(frozen=True)
class _AuthDeps:
    path_exists: Callable
    load_token: Callable
    refresh: Callable
    save_token: Callable
    run_flow: Callable


def _real_deps() -> _AuthDeps:  # pragma: no cover - wires real Google libs (live only)
    from pathlib import Path

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    return _AuthDeps(
        path_exists=os.path.exists,
        load_token=lambda token_path, scopes: Credentials.from_authorized_user_file(
            token_path, scopes
        ),
        refresh=lambda creds: creds.refresh(Request()),
        save_token=lambda token_path, creds: Path(token_path).write_text(
            creds.to_json(), encoding="utf-8"
        ),
        run_flow=lambda creds_path, scopes: InstalledAppFlow.from_client_secrets_file(
            creds_path, scopes
        ).run_local_server(port=0),
    )


def load_credentials(creds_path, token_path, scopes, *, run_auth, deps=None):
    """Return usable credentials or raise a controlled :class:`GmailAuthError`."""
    if deps is None:  # pragma: no cover - real deps only used in live mode
        deps = _real_deps()
    if token_path and deps.path_exists(token_path):
        creds = deps.load_token(token_path, scopes)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            deps.refresh(creds)
            deps.save_token(token_path, creds)
            return creds
    if not (creds_path and deps.path_exists(creds_path)):
        raise GmailAuthError("missing OAuth client secrets (set GOOGLE_OAUTH_CLIENT_SECRETS)")
    if not run_auth:
        raise GmailAuthError("token missing; set RUN_GMAIL_AUTH=1 to run the local OAuth flow")
    creds = deps.run_flow(creds_path, scopes)
    deps.save_token(token_path, creds)
    return creds
