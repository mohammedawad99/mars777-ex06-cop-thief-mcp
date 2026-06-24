"""Unit tests for cloud config and the role-aware runtime entrypoint."""

import json

import pytest

from mars777_cop_thief.deployment.cloud_config import (
    CloudConfigError,
    load_cloud_config,
    public_urls_are_placeholders,
)
from mars777_cop_thief.mcp_servers import cloud_entrypoint
from mars777_cop_thief.mcp_servers.cloud_entrypoint import (
    CloudRoleError,
    require_role_token,
    resolve_host,
    resolve_port,
    resolve_role,
)

_MCP = {
    "cop_server": {"token_env_var": "COP_MCP_TOKEN"},
    "thief_server": {"token_env_var": "THIEF_MCP_TOKEN"},
}


def test_cloud_config_loads_and_validates():
    config = load_cloud_config()
    assert config["target_platform"] == "google_cloud_run"
    assert config["services"]["cop"] == "mars777-cop-mcp"
    assert config["services"]["thief"] == "mars777-thief-mcp"
    assert config["live_deploy_enabled_env_var"] == "RUN_CLOUD_DEPLOY"


def test_cloud_config_not_deployed_with_placeholder_urls():
    config = load_cloud_config()
    assert config["cloud_status"] == "not_deployed"
    assert public_urls_are_placeholders(config)
    assert config["public_url_placeholders"]["cop"] == "<set-after-deployment>"


def test_public_urls_detected_as_non_placeholder():
    deployed = {"public_url_placeholders": {"cop": "https://cop.example.run.app"}}
    assert public_urls_are_placeholders(deployed) is False
    assert public_urls_are_placeholders({"public_url_placeholders": {}}) is False
    # Starts with "<" but is not a closed placeholder → still not a placeholder.
    assert public_urls_are_placeholders({"public_url_placeholders": {"cop": "<oops"}}) is False


def test_cloud_config_missing_field_raises(tmp_path):
    bad = tmp_path / "cloud.json"
    bad.write_text(json.dumps({"version": "1.00"}), encoding="utf-8")
    with pytest.raises(CloudConfigError, match="missing cloud config fields"):
        load_cloud_config(bad)


def test_role_resolver_accepts_cop_and_thief():
    assert resolve_role({"MCP_ROLE": "cop"}) == "cop"
    assert resolve_role({"MCP_ROLE": "thief"}) == "thief"
    assert resolve_role({"ROLE": "cop"}) == "cop"  # ROLE fallback


def test_role_resolver_rejects_unknown_role():
    with pytest.raises(CloudRoleError):
        resolve_role({"MCP_ROLE": "wizard"})
    with pytest.raises(CloudRoleError):
        resolve_role({})


def test_port_resolver_uses_port_env():
    assert resolve_port({"PORT": "9090"}) == 9090
    assert resolve_port({}) == 8080  # local default


def test_require_role_token_does_not_expose_value():
    token_var = require_role_token("cop", _MCP, {"COP_MCP_TOKEN": "super-secret-value"})
    assert token_var == "COP_MCP_TOKEN"  # the NAME, never the value


def test_missing_token_error_has_no_value():
    with pytest.raises(CloudRoleError) as info:
        require_role_token("thief", _MCP, {})  # token unset
    message = str(info.value)
    assert "THIEF_MCP_TOKEN" in message
    assert "super-secret-value" not in message


def test_resolve_host_defaults_to_all_interfaces():
    assert resolve_host({}) == "0.0.0.0"
    assert resolve_host({"MCP_BIND_HOST": "127.0.0.1"}) == "127.0.0.1"


def test_main_fails_safely_without_role(capsys):
    # No MCP_ROLE → controlled error, exit 1, no server started.
    assert cloud_entrypoint.main(env={}) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_main_fails_safely_when_token_missing(capsys):
    # Valid role but no token → reaches the token check, fails safely, no leak.
    assert cloud_entrypoint.main(env={"MCP_ROLE": "cop"}) == 1
    out = capsys.readouterr().out
    assert "COP_MCP_TOKEN" in out  # the env-var NAME, not a value
    assert json.loads(out)["status"] == "error"
