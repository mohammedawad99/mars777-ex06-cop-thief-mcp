"""Cloud deployment configuration loading (packaging only; no cloud calls).

Reads ``config/cloud.default.json`` — target platform, service placeholder names,
env-var names, public-URL placeholders, and the live-deploy gate. Holds no
secrets, no real project IDs, and no real URLs.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.shared.config import load_json_config

_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOUD_CONFIG_PATH = _ROOT / "config" / "cloud.default.json"

_REQUIRED = (
    "version",
    "target_platform",
    "services",
    "role_env_var",
    "port_env_var",
    "required_token_env_vars",
    "public_url_placeholders",
    "cloud_status",
    "deployment_region_placeholder",
    "secret_manager_note",
    "live_deploy_enabled_env_var",
)


class CloudConfigError(RuntimeError):
    """Raised when the cloud config is missing required fields."""


def load_cloud_config(path: str | Path | None = None) -> dict:
    """Load and validate the cloud deployment config."""
    config = load_json_config(path or DEFAULT_CLOUD_CONFIG_PATH)
    missing = [key for key in _REQUIRED if key not in config]
    if missing:
        raise CloudConfigError(f"missing cloud config fields: {', '.join(missing)}")
    return config


def public_urls_are_placeholders(config: dict) -> bool:
    """True only when every public URL is still a ``<placeholder>`` (not deployed)."""
    values = list(config.get("public_url_placeholders", {}).values())
    if not values:
        return False
    return all(str(v).startswith("<") and str(v).endswith(">") for v in values)
