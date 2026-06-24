"""Unit tests for the inter-group bonus partner-intake validation (pure, no IO)."""

from mars777_cop_thief.bonus.intake import (
    REQUIRED_FIELDS,
    is_placeholder,
    normalize_mcp,
    validate_partner,
)

_REAL = {
    "partner_group_code": "OtherGroup-42",
    "partner_group_slug": "other42",
    "partner_github_repo": "https://github.com/other/repo",
    "partner_cop_mcp_url": "https://other-cop.example.app",
    "partner_thief_mcp_url": "https://other-thief.example.app/mcp/",
    "partner_cop_token": "real-cop-token",
    "partner_thief_token": "real-thief-token",
    "partner_students_public": [{"name": "A"}, {"name": "B"}],
    "agreement_channel": "email",
}


def test_is_placeholder_variants():
    assert is_placeholder("<PARTNER>") is True
    assert is_placeholder("") is True
    assert is_placeholder("   ") is True
    assert is_placeholder(None) is True
    assert is_placeholder(123) is True
    assert is_placeholder("real-value") is False


def test_normalize_mcp_appends_and_strips():
    assert normalize_mcp("https://x.app") == "https://x.app/mcp"
    assert normalize_mcp("https://x.app/mcp") == "https://x.app/mcp"
    assert normalize_mcp("https://x.app/mcp/") == "https://x.app/mcp"


def test_validate_partner_complete_real_data():
    intake, urls, info, blockers = validate_partner(_REAL)
    assert intake is True
    assert urls is True
    assert blockers == []
    assert info["partner_group_code"] == "OtherGroup-42"
    assert info["partner_cop_mcp_url"] == "https://other-cop.example.app/mcp"
    assert info["partner_thief_mcp_url"] == "https://other-thief.example.app/mcp"
    assert info["partner_students_count"] == 2
    assert info["partner_cop_token_present"] is True
    assert info["partner_thief_token_present"] is True
    # no token VALUES leak into the public info dict
    assert "real-cop-token" not in str(info)
    assert "real-thief-token" not in str(info)


def test_validate_partner_all_placeholders():
    data = {k: f"<{k}>" for k in REQUIRED_FIELDS}
    intake, urls, info, blockers = validate_partner(data)
    assert intake is False
    assert urls is False
    assert any("incomplete" in b for b in blockers)
    assert info["partner_group_code"] is None
    assert info["partner_cop_mcp_url"] is None
    assert info["partner_students_count"] == 0
    assert info["partner_cop_token_present"] is False


def test_validate_partner_non_http_urls_rejected():
    data = dict(_REAL)
    data["partner_cop_mcp_url"] = "ftp://nope"
    data["partner_thief_mcp_url"] = "ftp://nope2"
    intake, urls, info, blockers = validate_partner(data)
    assert urls is False
    assert any("not valid http" in b for b in blockers)
    assert info["partner_cop_mcp_url"] is None
