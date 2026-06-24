"""Fixtures for the reporting tests: a deterministic sample MCP report."""

import pytest


def _sub_game(index: int, winner: str) -> dict:
    cop_score, thief_score = (20, 5) if winner == "cop" else (5, 10)
    return {
        "index": index,
        "board": {"rows": 5, "cols": 5},
        "winner": winner,
        "scores": {"cop": cop_score, "thief": thief_score},
        "start": {"cop": {"row": 0, "col": 0}, "thief": {"row": 4, "col": 4}},
        "final": {"cop": {"row": 2, "col": 2}, "thief": {"row": 3, "col": 4}},
        "move_count": 25,
        "barriers": [],
        "events": [{"ok": True} for _ in range(25)],
        "transcript": [
            {
                "turn_index": 0,
                "sender": "thief",
                "recipient": "cop",
                "message": "I cannot see the cop right now; I am staying cautious and exploring.",
                "opponent_visible": False,
                "audit": {"opponent_visible": False, "leaked": False},
            },
            {
                "turn_index": 1,
                "sender": "cop",
                "recipient": "thief",
                "message": "I cannot see the thief right now; I am guarding nearby corridors.",
                "opponent_visible": False,
                "audit": {"opponent_visible": False, "leaked": False},
            },
        ],
    }


@pytest.fixture
def mcp_report() -> dict:
    return {
        "stage": "local-self-play",
        "mode": "mcp-backed",
        "group_code": "MaRs-777",
        "group_slug": "mars777",
        "github_repo": "REPLACE_WITH_GITHUB_REPO_URL",
        "timezone": "Asia/Jerusalem",
        "config": {
            "grid_size": [5, 5],
            "max_moves": 25,
            "num_sub_games": 6,
            "max_barriers": 5,
            "allow_stay": False,
            "turn_order": ["thief", "cop"],
            "visibility_radius": 1,
            "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
        },
        "sub_games": [_sub_game(0, "thief"), _sub_game(1, "cop")],
        "totals": {"cop": 25, "thief": 15},
        "win_counts": {"cop": 1, "thief": 1, "none": 0},
        "transport": "local_mcp_http",
        "mcp_status": "local_verified",
        "cop_mcp_url": "http://127.0.0.1:54321/mcp",
        "thief_mcp_url": "http://127.0.0.1:54322/mcp",
        "cloud_status": "not_deployed",
        "email_status": "not_sent",
        "hidden_state_respected": True,
    }
