"""In-memory, JSON-serializable report builder for local self-play.

This is the Stage 3 local backbone report. It is **local-only**: MCP servers are
not deployed and nothing is emailed, so ``mcp_status`` is explicitly
``not-deployed`` and no cloud/Gmail readiness is claimed.
"""

from __future__ import annotations

from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.orchestration.totals import total_scores, win_counts

_GITHUB_PLACEHOLDER = "REPLACE_WITH_GITHUB_REPO_URL"


def _config_summary(config: dict) -> dict:
    return {
        "grid_size": config["grid_size"],
        "max_moves": config["max_moves"],
        "num_sub_games": config["num_sub_games"],
        "max_barriers": config["max_barriers"],
        "allow_stay": config["allow_stay"],
        "turn_order": config["turn_order"],
        "scoring": config["scoring"],
    }


def build_report(config: dict, results: list[SubGameResult]) -> dict:
    """Assemble a JSON-serializable local self-play report dictionary."""
    return {
        "stage": "local-self-play",
        "mode": "deterministic-baseline",
        "mcp_status": "not-deployed",
        "group_code": config["group_code"],
        "group_slug": config["group_slug"],
        "github_repo": config.get("github_repo", _GITHUB_PLACEHOLDER),
        "timezone": config["timezone"],
        "config": _config_summary(config),
        "sub_games": [result.to_dict() for result in results],
        "totals": total_scores(results),
        "win_counts": win_counts(results),
    }
