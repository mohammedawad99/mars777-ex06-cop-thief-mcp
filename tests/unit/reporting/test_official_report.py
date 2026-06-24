"""Unit tests for the official internal and bonus report builders."""

import json

from mars777_cop_thief.reporting.official_report import (
    build_bonus_report_example,
    build_official_internal_report,
)
from mars777_cop_thief.reporting.schemas import (
    INTERNAL_REQUIRED_SUBGAME,
    INTERNAL_REQUIRED_TOP,
    INTERNAL_REQUIRED_TOTALS,
)


def test_internal_report_has_required_fields_and_is_valid(mcp_report):
    report = build_official_internal_report(mcp_report)
    assert report["report_type"] == "internal_game"
    assert set(INTERNAL_REQUIRED_TOP) <= set(report)
    assert set(INTERNAL_REQUIRED_TOTALS) <= set(report["totals"])
    for sub_game in report["sub_games"]:
        assert set(INTERNAL_REQUIRED_SUBGAME) <= set(sub_game)
    assert report["validation_status"] == "valid"


def test_internal_report_is_json_serializable(mcp_report):
    assert json.dumps(build_official_internal_report(mcp_report))


def test_internal_report_totals_and_outcomes(mcp_report):
    report = build_official_internal_report(mcp_report)
    assert report["totals"]["cop_score"] == 25
    assert report["totals"]["thief_score"] == 15
    assert report["totals"]["cop_wins"] == 1
    assert report["totals"]["thief_wins"] == 1
    assert report["totals"]["sub_games_completed"] == 2
    reasons = {s["sub_game_index"]: s["outcome_reason"] for s in report["sub_games"]}
    assert reasons[0] == "thief_survived_max_moves"
    assert reasons[1] == "capture"


def test_outcome_reason_terminal_when_not_capture_or_max_moves(mcp_report):
    # Thief winner but move_count below max_moves → generic "terminal" outcome.
    mcp_report["sub_games"][0]["winner"] = "thief"
    mcp_report["sub_games"][0]["move_count"] = 3
    report = build_official_internal_report(mcp_report)
    assert report["sub_games"][0]["outcome_reason"] == "terminal"


def test_students_are_configurable(mcp_report):
    students = [{"name": "Mohamed Awad", "id": "123"}]
    report = build_official_internal_report(mcp_report, students=students)
    assert report["students"] == students


def test_bonus_example_is_serializable_and_makes_no_claim():
    bonus = build_bonus_report_example()
    assert json.dumps(bonus)
    assert bonus["report_type"] == "bonus_game"
    assert bonus["bonus_claim"] is False
    assert bonus["mutual_agreement"] is False
    assert bonus["status"] == "schema_example_only"
    assert "no real inter-group game" in bonus["note"].lower()
