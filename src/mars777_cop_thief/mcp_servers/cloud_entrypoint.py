"""Role-aware cloud entrypoint for the MCP servers (no secrets, no cloud calls).

A single container image runs either the Cop or the Thief server, selected by the
``MCP_ROLE`` (or ``ROLE``) env var. In cloud mode it binds ``0.0.0.0`` and reads
``PORT``; locally the existing per-role entrypoints still bind ``127.0.0.1``. The
role's token env var must be present; its value is never read here or logged.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mars777_cop_thief.mcp_servers.cop_server import build_cop_server
from mars777_cop_thief.mcp_servers.thief_server import build_thief_server
from mars777_cop_thief.shared.config import load_game_config, load_json_config

_ROOT = Path(__file__).resolve().parents[3]
GAME_CONFIG_PATH = _ROOT / "config" / "game.default.json"
MCP_CONFIG_PATH = _ROOT / "config" / "mcp.local.default.json"
_ROLES = ("cop", "thief")
_BUILDERS = {"cop": build_cop_server, "thief": build_thief_server}


class CloudRoleError(RuntimeError):
    """Raised when the role/token environment is not correctly configured."""


def resolve_role(env, *, role_env_var: str = "MCP_ROLE") -> str:
    """Resolve and validate the server role from the environment."""
    role = (env.get(role_env_var) or env.get("ROLE") or "").strip().lower()
    if role not in _ROLES:
        raise CloudRoleError(f"{role_env_var} must be one of {_ROLES}; got: {role or '(unset)'}")
    return role


def resolve_port(env, *, port_env_var: str = "PORT", default: int = 8080) -> int:
    """Use ``PORT`` (set by the cloud platform) when present, else a local default."""
    value = env.get(port_env_var)
    return int(value) if value else default


def resolve_host(env, *, default: str = "0.0.0.0") -> str:
    """Bind 0.0.0.0 in cloud mode (overridable for local use)."""
    return env.get("MCP_BIND_HOST", default)


def require_role_token(role: str, mcp_config: dict, env) -> str:
    """Confirm the role's token env var is set; return its NAME (never its value)."""
    token_var = mcp_config[f"{role}_server"]["token_env_var"]
    if not env.get(token_var):
        raise CloudRoleError(f"missing token env var {token_var} for role '{role}'")
    return token_var


def _serve(role, mcp_config, env) -> None:  # pragma: no cover - starts a long-running server
    server = _BUILDERS[role](load_game_config(GAME_CONFIG_PATH), mcp_config)
    path = mcp_config[f"{role}_server"]["path"]
    server.run(
        transport=mcp_config["transport"], host=resolve_host(env), port=resolve_port(env), path=path
    )


def main(env=None) -> int:
    env = env if env is not None else os.environ
    try:
        role = resolve_role(env)
        mcp_config = load_json_config(MCP_CONFIG_PATH)
        require_role_token(role, mcp_config, env)
    except CloudRoleError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1
    _serve(role, mcp_config, env)  # pragma: no cover - long-running server
    return 0  # pragma: no cover - reached only after the server runs


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
