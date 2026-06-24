"""Fixtures for the run-hardening tests: a deterministic prompted report."""

import pytest

from mars777_cop_thief.reporting.official_report import build_official_internal_report


def _sub_game(index: int) -> dict:
    return {
        "index": index,
        "board": {"rows": 5, "cols": 5},
        "winner": "thief",
        "scores": {"cop": 5, "thief": 10},
        "start": {"cop": {"row": 0, "col": 0}, "thief": {"row": 4, "col": 4}},
        "final": {"cop": {"row": 2, "col": 2}, "thief": {"row": 3, "col": 4}},
        "move_count": 25,
        "barriers": [],
        "events": [{"ok": True} for _ in range(25)],
        "transcript": [{"turn_index": 0, "audit": {"leaked": False}, "message": "no view"}],
    }


@pytest.fixture
def prompted_report() -> dict:
    """A prompted-shaped report with 2 sub-games (mirrors build_prompted_report)."""
    return {
        "mode": "mcp-backed-prompted",
        "group_code": "MaRs-777",
        "group_slug": "mars777",
        "github_repo": "REPLACE_WITH_GITHUB_REPO_URL",
        "timezone": "Asia/Jerusalem",
        "config": {
            "grid_size": [5, 5],
            "max_moves": 25,
            "num_sub_games": 2,
            "max_barriers": 5,
            "allow_stay": False,
            "turn_order": ["thief", "cop"],
            "visibility_radius": 1,
            "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
        },
        "sub_games": [_sub_game(0), _sub_game(1)],
        "totals": {"cop": 10, "thief": 20},
        "win_counts": {"cop": 0, "thief": 2, "none": 0},
        "transport": "local_mcp_http",
        "mcp_status": "local_verified",
        "cop_mcp_url": "http://127.0.0.1:8001/mcp",
        "thief_mcp_url": "http://127.0.0.1:8002/mcp",
        "cloud_status": "not_deployed",
        "email_status": "not_sent",
        "hidden_state_respected": True,
        "passed": True,
    }


@pytest.fixture
def official_report(prompted_report) -> dict:
    return build_official_internal_report(prompted_report)
