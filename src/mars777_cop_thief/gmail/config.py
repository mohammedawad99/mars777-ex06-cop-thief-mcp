"""Gmail report-sender configuration loading.

Reads ``config/gmail.default.json`` — recipient, subject template, send scope, and
the *names* of the env vars that carry OAuth file paths and the live/auth gates.
Holds no secrets and never requires the OAuth files at import or load time.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.shared.config import load_json_config

_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GMAIL_CONFIG_PATH = _ROOT / "config" / "gmail.default.json"

_REQUIRED = (
    "version",
    "recipient",
    "subject_template",
    "send_scope",
    "credentials_path_env_var",
    "token_path_env_var",
    "run_live_env_var",
    "run_auth_env_var",
    "default_mode",
    "body_format",
)


class GmailConfigError(RuntimeError):
    """Raised when the Gmail configuration is missing required fields."""


def load_gmail_config(path: str | Path | None = None) -> dict:
    """Load and validate the Gmail config (no OAuth files are touched)."""
    config = load_json_config(path or DEFAULT_GMAIL_CONFIG_PATH)
    missing = [key for key in _REQUIRED if key not in config]
    if missing:
        raise GmailConfigError(f"missing gmail config fields: {', '.join(missing)}")
    return config


def resolve_recipient(config: dict, env) -> str:
    """Recipient from the env override, else the configured default."""
    return env.get(config.get("recipient_env_var", "GMAIL_REPORT_RECIPIENT")) or config["recipient"]


def resolve_paths(config: dict, env) -> tuple[str | None, str | None]:
    """Return ``(credentials_path, token_path)`` from env (may be ``None``)."""
    return env.get(config["credentials_path_env_var"]), env.get(config["token_path_env_var"])
