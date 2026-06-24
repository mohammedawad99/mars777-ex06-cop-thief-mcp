"""Gmail OAuth external-file readiness preflight (no Gmail API, no content reads).

Checks only that the OAuth client-secrets and token files named by
``GOOGLE_OAUTH_CLIENT_SECRETS`` / ``GOOGLE_OAUTH_TOKEN_PATH`` exist, live OUTSIDE
the repository, and look like the expected filenames. It never opens the files,
never prints their contents or full paths, and never calls Gmail. Live sending
stays gated by ``RUN_GMAIL_LIVE=1`` and is not triggered here.
"""

from __future__ import annotations

import os
from pathlib import Path

from mars777_cop_thief.gmail.config import load_gmail_config, resolve_paths

_ROOT = Path(__file__).resolve().parents[3]

_EXPECTED_NAMES = {"credentials": ("credentials.json",), "token": ("token.json",)}


def _is_outside(path: Path, root: Path) -> bool:
    """True when ``path`` does not resolve inside the repository ``root``."""
    try:
        path.resolve().relative_to(root.resolve())
        return False
    except ValueError:
        return True


def _name_warning(path: str, expected: tuple[str, ...], label: str) -> str | None:
    name = Path(path).name
    if name in expected:
        return None
    return f"{label} filename is not {expected[0]} (safe alternative — verify intentionally)"


def run_gmail_preflight(env=None, root=None) -> dict:
    """Check external OAuth files by existence/location only; return JSON-safe dict."""
    env = env if env is not None else os.environ
    root = Path(root) if root is not None else _ROOT
    config = load_gmail_config()
    creds_path, token_path = resolve_paths(config, env)
    blockers: list[str] = []
    warnings: list[str] = []

    creds_exists = bool(creds_path) and Path(creds_path).is_file()
    token_exists = bool(token_path) and Path(token_path).is_file()
    _record_existence(creds_path, creds_exists, "client-secrets", blockers)
    _record_existence(token_path, token_exists, "token", blockers)

    outside_repo = _check_outside(creds_path, token_path, root, blockers, warnings)

    live_send_enabled = env.get(config["run_live_env_var"]) == "1"
    if live_send_enabled:
        warnings.append("RUN_GMAIL_LIVE=1 set; this preflight still sends nothing")

    return {
        "status": "ready" if not blockers else "blocked",
        "credentials_file_exists": creds_exists,
        "token_file_exists": token_exists,
        "outside_repo": outside_repo,
        "live_send_enabled": live_send_enabled,
        "blockers": blockers,
        "warnings": warnings,
    }


def _record_existence(path, exists: bool, label: str, blockers: list[str]) -> None:
    if not path:
        blockers.append(f"{label} path env var is not set")
    elif not exists:
        blockers.append(f"{label} file does not exist (checked by path only)")


def _check_outside(creds_path, token_path, root, blockers, warnings) -> bool:
    outside = True
    for label, path in (("credentials", creds_path), ("token", token_path)):
        if not path:
            continue
        if not _is_outside(Path(path), root):
            outside = False
            blockers.append(f"{label} path is INSIDE the repository; keep it outside Git")
        note = _name_warning(path, _EXPECTED_NAMES[label], label)
        if note:
            warnings.append(note)
    return outside
