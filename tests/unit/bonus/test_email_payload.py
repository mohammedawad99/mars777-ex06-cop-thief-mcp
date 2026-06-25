"""Unit tests for the final bonus_game email payload checks (pure, no IO/network)."""

import json

from mars777_cop_thief.bonus.bonus_handoff import result_hash
from mars777_cop_thief.bonus.bonus_report import build_bonus_game_report
from mars777_cop_thief.bonus.email_payload import (
    EXPECTED_RECIPIENT,
    payload_is_safe,
    pre_send_checks,
    with_result_hash,
)
from mars777_cop_thief.bonus.finalize import finalize_agreement
from mars777_cop_thief.game.models import Position
from mars777_cop_thief.orchestration.results import SubGameResult

PARTNER = {"group_code": "orcai-mj", "group_slug": "orcai-mj"}
URLS = {f"group_{g}_{r}": f"https://{g}-{r}/mcp" for g in ("a", "b") for r in ("cop", "thief")}
REPOS = {"ours": "https://github.com/ours", "partner": "https://github.com/partner"}
STUDENTS = {"group_a": [{"name": "Alice", "id": "REDACTED"}], "group_b": [{"name": "Bob"}]}


def _sg(index, winner, scores, move_count):
    return SubGameResult(
        index=index,
        rows=8,
        cols=8,
        winner=winner,
        scores=scores,
        cop_start=Position(0, 0),
        thief_start=Position(7, 7),
        cop_final=Position(2, 2),
        thief_final=Position(4, 7),
        move_count=move_count,
        barriers=[],
        events=[{"ok": True}],
        transcript=[{"message": "hi"}],
    )


def _agreed():
    a = [_sg(i, "thief", {"cop": 5, "thief": 10}, 25) for i in range(3)]
    b = [_sg(i + 3, "cop", {"cop": 20, "thief": 5}, 14) for i in range(3)]
    report = build_bonus_game_report(
        a,
        b,
        [None] * 3,
        [None] * 3,
        partner=PARTNER,
        urls=URLS,
        repos=REPOS,
        students=STUDENTS,
        generated_at_iso="2026-06-25T19:32:37+03:00",
    )
    return finalize_agreement(report, notes="confirmed")


def test_expected_recipient_is_the_lecturer():
    assert EXPECTED_RECIPIENT == "rmisegal+uoh26b@gmail.com"


def test_pre_send_checks_all_pass_for_agreed_report():
    checks = pre_send_checks(_agreed())
    assert all(checks.values())
    assert set(checks) >= {"report_type_bonus_game", "mutual_agreement_true", "board_8x8"}


def test_pre_send_checks_fail_when_not_agreed():
    report = _agreed()
    report["mutual_agreement"] = False
    report["totals_by_group"]["orcai-mj"]["score"] = 80
    checks = pre_send_checks(report)
    assert checks["mutual_agreement_true"] is False
    assert checks["orcai_total_90"] is False


def test_with_result_hash_adds_field_without_changing_outcome():
    agreed = _agreed()
    payload = with_result_hash(agreed)
    assert payload["result_hash"] == result_hash(agreed)
    assert "result_hash" not in agreed  # original not mutated
    # outcome-bearing fields are identical, so the digest is unchanged
    assert result_hash(payload) == result_hash(agreed)
    assert payload["sub_games"] == agreed["sub_games"]


def test_payload_is_safe_for_clean_report():
    payload = with_result_hash(_agreed())
    assert payload_is_safe(payload) == []
    assert json.loads(json.dumps(payload))  # round-trips as JSON


def test_payload_is_unsafe_flags_id_token_and_secrets_path():
    payload = with_result_hash(_agreed())
    payload["group_a"]["students"][0]["id"] = "12345" + "6789"  # runtime 9-digit; no literal run
    payload["leak"] = "/home/u/.secrets/students.local.json"
    payload["auth_token"] = "abc"
    issues = payload_is_safe(payload)
    assert any("9-digit" in i for i in issues)
    assert any(".secrets" in i for i in issues)
    assert any("token" in i for i in issues)
