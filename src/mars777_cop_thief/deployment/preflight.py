"""Cloud deployment preflight (packaging readiness only; never calls the cloud).

Validates the cloud config, the Docker packaging, the absence of secret files, and
that role/port resolve without starting a server. Prints a JSON result and exits 0
only when packaging is ready. It does not require gcloud, credentials, or network.
"""

from __future__ import annotations

import json
from pathlib import Path

from mars777_cop_thief.deployment.cloud_config import (
    load_cloud_config,
    public_urls_are_placeholders,
)
from mars777_cop_thief.deployment.docker_checks import (
    dockerfile_exists,
    dockerignore_exists,
    find_forbidden_secret_files,
    missing_dockerignore_entries,
)
from mars777_cop_thief.mcp_servers.cloud_entrypoint import (
    CloudRoleError,
    resolve_port,
    resolve_role,
)

_ROOT = Path(__file__).resolve().parents[3]


def _role_resolution_ok() -> bool:
    try:
        resolve_role({})  # a missing role must raise
        return False  # pragma: no cover - resolve_role always raises on empty
    except CloudRoleError:
        pass
    return (
        resolve_role({"MCP_ROLE": "cop"}) == "cop"
        and resolve_role({"MCP_ROLE": "thief"}) == "thief"
        and resolve_port({"PORT": "9090"}) == 9090
    )


def _commands_documented(root: Path) -> bool:
    guide = root / "docs" / "CLOUD_DEPLOYMENT.md"
    readme = root / "README.md"
    if not (guide.is_file() and readme.is_file()):
        return False
    text = readme.read_text(encoding="utf-8")
    return "deployment.preflight" in text and "hardened_smoke" in text and "game_smoke" in text


def run_preflight(root: str | Path | None = None) -> dict:
    """Run packaging-readiness checks and return a JSON-serializable result."""
    root = Path(root) if root is not None else _ROOT
    config = load_cloud_config()
    checks = {
        "cloud_config_valid": True,
        "cloud_status_not_deployed": config["cloud_status"] == "not_deployed",
        "public_urls_are_placeholders": public_urls_are_placeholders(config),
        "dockerfile_present": dockerfile_exists(root),
        "dockerignore_present": dockerignore_exists(root),
        "dockerignore_covers_secrets": not missing_dockerignore_entries(root),
        "no_forbidden_secret_files": not find_forbidden_secret_files(root),
        "role_port_resolves_without_server": _role_resolution_ok(),
        "smoke_commands_documented": _commands_documented(root),
    }
    passed = all(checks.values())
    return {
        "status": "ok" if passed else "failed",
        "passed": passed,
        "target_platform": config["target_platform"],
        "cloud_status": config["cloud_status"],
        "services": config["services"],
        "checks": checks,
    }


def main() -> int:
    result = run_preflight()
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
