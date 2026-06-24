"""Build the official internal report (and a bonus schema example).

Transforms a Stage 7 MCP-backed report into the stable, validated internal
schema. The bonus example is schema-only — it does **not** claim any real
inter-group game has been played.
"""

from __future__ import annotations

from mars777_cop_thief.reporting.schemas import (
    BONUS_REPORT_TYPE,
    DEFAULT_STUDENTS,
    GENERATED_AT_PLACEHOLDER,
    INTERNAL_REPORT_TYPE,
    SCHEMA_VERSION,
)
from mars777_cop_thief.reporting.validators import validate_internal_report


def _outcome_reason(sub_game: dict, max_moves: int) -> str:
    if sub_game["winner"] == "cop":
        return "capture"
    if sub_game["move_count"] >= max_moves:
        return "thief_survived_max_moves"
    return "terminal"


def _transcript_summary(transcript: list[dict]) -> dict:
    return {
        "message_count": len(transcript),
        "first_message": transcript[0]["message"] if transcript else None,
        "last_message": transcript[-1]["message"] if transcript else None,
    }


def _sub_game(sub_game: dict, max_moves: int) -> dict:
    return {
        "sub_game_index": sub_game["index"],
        "board_size": [sub_game["board"]["rows"], sub_game["board"]["cols"]],
        "max_moves": max_moves,
        "start_positions": sub_game["start"],
        "final_positions": sub_game["final"],
        "winner": sub_game["winner"],
        "move_count": sub_game["move_count"],
        "cop_score": sub_game["scores"]["cop"],
        "thief_score": sub_game["scores"]["thief"],
        "barriers": sub_game["barriers"],
        "transcript_summary": _transcript_summary(sub_game["transcript"]),
        "event_count": len(sub_game["events"]),
        "outcome_reason": _outcome_reason(sub_game, max_moves),
    }


def _totals(mcp_report: dict, completed: int) -> dict:
    wins, totals = mcp_report["win_counts"], mcp_report["totals"]
    return {
        "cop_score": totals["cop"],
        "thief_score": totals["thief"],
        "cop_wins": wins["cop"],
        "thief_wins": wins["thief"],
        "sub_games_completed": completed,
        "invalid_sub_games": wins.get("none", 0),
        "scoring_summary": {
            "cop_win": "cop 20 / thief 5",
            "thief_win": "thief 10 / cop 5",
            "team_total_bounds_over_6": [30, 90],
        },
    }


def build_official_internal_report(mcp_report: dict, students=None, generated_at_iso=None) -> dict:
    """Build a validated official internal report from an MCP-backed report."""
    max_moves = mcp_report["config"]["max_moves"]
    sub_games = [_sub_game(s, max_moves) for s in mcp_report["sub_games"]]
    report = {
        "report_type": INTERNAL_REPORT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "group_code": mcp_report["group_code"],
        "group_slug": mcp_report["group_slug"],
        "students": list(students) if students else list(DEFAULT_STUDENTS),
        "github_repo": mcp_report["github_repo"],
        "cop_mcp_url": mcp_report["cop_mcp_url"],
        "thief_mcp_url": mcp_report["thief_mcp_url"],
        "mcp_status": mcp_report["mcp_status"],
        "cloud_status": mcp_report["cloud_status"],
        "email_status": mcp_report["email_status"],
        "timezone": mcp_report["timezone"],
        "config_summary": mcp_report["config"],
        "sub_games": sub_games,
        "totals": _totals(mcp_report, len(sub_games)),
        "evidence": {
            "transport": mcp_report.get("transport"),
            "hidden_state_respected": mcp_report.get("hidden_state_respected"),
        },
        "generated_at_iso": generated_at_iso or GENERATED_AT_PLACEHOLDER,
        "validation_status": "pending",
    }
    report["validation_status"] = "valid" if not validate_internal_report(report) else "invalid"
    return report


def build_bonus_report_example() -> dict:
    """Return a placeholder bonus schema example (no real game claimed)."""
    return {
        "report_type": BONUS_REPORT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "status": "schema_example_only",
        "note": "Placeholder bonus schema. No real inter-group game has been run.",
        "group_a": {"group_code": "MaRs-777", "group_slug": "mars777"},
        "group_b": {"group_code": "REPLACE_WITH_OTHER_GROUP", "group_slug": "replace_me"},
        "github_repos": {"group_a": "REPLACE_WITH_REPO", "group_b": "REPLACE_WITH_REPO"},
        "mcp_urls": {
            "group_a_cop": "REPLACE_WITH_URL",
            "group_a_thief": "REPLACE_WITH_URL",
            "group_b_cop": "REPLACE_WITH_URL",
            "group_b_thief": "REPLACE_WITH_URL",
        },
        "timezone": "Asia/Jerusalem",
        "students": {"group_a": list(DEFAULT_STUDENTS), "group_b": list(DEFAULT_STUDENTS)},
        "sub_games": [],
        "totals_by_group": {"group_a": {"cop_score": 0, "thief_score": 0}, "group_b": {}},
        "bonus_claim": False,
        "mutual_agreement": False,
        "agreement_notes": "Not yet played; both groups must agree first.",
        "validation_status": "schema_example",
    }
