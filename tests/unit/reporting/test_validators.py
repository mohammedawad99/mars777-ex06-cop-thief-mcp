"""Unit tests for report validation and token-safety scanning."""

from mars777_cop_thief.reporting.official_report import (
    build_bonus_report_example,
    build_official_internal_report,
)
from mars777_cop_thief.reporting.validators import (
    find_token_like,
    is_valid_internal_report,
    validate_bonus_report,
    validate_internal_report,
)


def test_valid_report_passes(mcp_report):
    assert validate_internal_report(build_official_internal_report(mcp_report)) == []


def test_missing_top_field_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    del report["totals"]
    errors = validate_internal_report(report)
    assert any("missing top field: totals" in e for e in errors)


def test_missing_sub_game_field_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    del report["sub_games"][0]["winner"]
    errors = validate_internal_report(report)
    assert any("sub_game[0] missing: winner" in e for e in errors)


def test_token_like_key_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    report["evidence"]["auth_token"] = "x"
    assert any("forbidden key" in e for e in validate_internal_report(report))


def test_token_like_value_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    report["evidence"]["note"] = "here is my secret password value"
    assert any("forbidden value" in e for e in validate_internal_report(report))


def test_dummy_token_value_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    report["evidence"]["leak"] = "dummy-local-cop-token"
    assert find_token_like(report)


def test_local_url_only_allowed_for_local_cloud_status(mcp_report):
    report = build_official_internal_report(mcp_report)
    assert validate_internal_report(report) == []  # not_deployed + local URL → ok
    report["cloud_status"] = "deployed"  # non-local but URLs still local → error
    assert any("local URL not allowed" in e for e in validate_internal_report(report))


def test_wrong_report_type_rejected(mcp_report):
    report = build_official_internal_report(mcp_report)
    report["report_type"] = "something_else"
    assert any("report_type must be internal_game" in e for e in validate_internal_report(report))


def test_is_valid_internal_report(mcp_report):
    report = build_official_internal_report(mcp_report)
    assert is_valid_internal_report(report) is True
    del report["totals"]
    assert is_valid_internal_report(report) is False


def test_bonus_report_validates(mcp_report):
    assert validate_bonus_report(build_bonus_report_example()) == []


def test_bonus_wrong_report_type_rejected():
    bonus = build_bonus_report_example()
    bonus["report_type"] = "internal_game"
    assert any("report_type must be bonus_game" in e for e in validate_bonus_report(bonus))
