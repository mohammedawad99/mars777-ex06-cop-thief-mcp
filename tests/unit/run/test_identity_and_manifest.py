"""Unit tests for run identity, config fingerprinting, and the manifest."""

import json

from mars777_cop_thief.run.identity import build_run_identity, config_fingerprint
from mars777_cop_thief.run.manifest import build_manifest, scan_manifest_secrets

CONFIG = {"group_slug": "mars777", "grid_size": [5, 5], "max_moves": 25, "num_sub_games": 6}


def _identity():
    return build_run_identity(
        CONFIG,
        stage="hardened",
        mode="mcp-backed-prompted",
        seed=0,
        created_at_utc="2026-01-01T00:00:00+00:00",
        git_commit="abc123",
    )


def test_identity_is_deterministic_when_injected():
    first, second = _identity(), _identity()
    assert first == second
    assert first.run_id == "mars777-hardened-" + first.config_hash + "-seed0"
    assert first.created_at_utc == "2026-01-01T00:00:00+00:00"
    assert first.git_commit == "abc123"


def test_config_fingerprint_changes_with_config():
    base = config_fingerprint(CONFIG)
    assert config_fingerprint(CONFIG) == base  # stable / order-independent
    assert config_fingerprint({**CONFIG, "max_moves": 10}) != base


def test_manifest_is_json_serializable_and_lists_capabilities():
    manifest = build_manifest(_identity(), {"num_sub_games": 6}, validation_gates={"x": "run"})
    assert json.dumps(manifest)
    assert manifest["capabilities_enabled"]["game_engine"] is True
    assert manifest["capabilities_enabled"]["local_mcp_http"] is True
    assert manifest["capabilities_disabled"]["cloud_public_urls"] is False
    assert manifest["capabilities_disabled"]["live_gmail_send"] is False
    assert manifest["capabilities_disabled"]["real_intergroup_bonus"] is False


def test_manifest_has_no_token_like_content():
    manifest = build_manifest(_identity(), {"num_sub_games": 6}, validation_gates={})
    # The scan-status meta fields are exempt; everything else must be token-free.
    assert scan_manifest_secrets(manifest) == []
