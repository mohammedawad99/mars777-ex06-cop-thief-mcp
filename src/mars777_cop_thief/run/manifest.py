"""JSON-serializable run manifest: capabilities, gates, and scan status.

The manifest references only the run identity, a config summary, capability flags,
validation gates, and scan results — never any secret. ``capabilities_disabled``
records features that are not active yet (cloud, live Gmail, inter-group).
"""

from __future__ import annotations

from mars777_cop_thief.reporting.validators import find_token_like
from mars777_cop_thief.run.identity import RunIdentity

MANIFEST_VERSION = "1.0"

# Meta fields whose names legitimately contain scan words (not secrets themselves).
_SCAN_EXEMPT_KEYS = ("secret_scan_status", "overclaim_scan_status")

_ENABLED_CAPABILITIES = (
    "game_engine",
    "partial_observability",
    "local_mcp_http",
    "fake_local_llm",
    "optional_gemini_provider",
    "gmail_dry_run",
)


def build_manifest(
    identity: RunIdentity,
    config_summary: dict,
    *,
    validation_gates: dict,
    artifact_paths=None,
    secret_scan_status: str = "clean",
    overclaim_scan_status: str = "clean",
    warnings=None,
    live_gmail: bool = False,
) -> dict:
    """Assemble a manifest describing one hardened run."""
    return {
        "manifest_version": MANIFEST_VERSION,
        "run_identity": identity.to_dict(),
        "config_summary": config_summary,
        "capabilities_enabled": dict.fromkeys(_ENABLED_CAPABILITIES, True),
        "capabilities_disabled": {
            "cloud_public_urls": False,
            "live_gmail_send": bool(live_gmail),
            "real_intergroup_bonus": False,
        },
        "validation_gates": validation_gates,
        "artifact_paths": list(artifact_paths or []),
        "secret_scan_status": secret_scan_status,
        "overclaim_scan_status": overclaim_scan_status,
        "warnings": list(warnings or []),
    }


def scan_manifest_secrets(manifest: dict) -> list[str]:
    """Token-scan the manifest, exempting the scan-status meta field names."""
    payload = {key: value for key, value in manifest.items() if key not in _SCAN_EXEMPT_KEYS}
    return find_token_like(payload, "manifest")
