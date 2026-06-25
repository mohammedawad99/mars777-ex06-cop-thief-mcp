"""Unit tests for the canonical bonus_game report, hashing, and handoff (pure)."""

from mars777_cop_thief.bonus.bonus_handoff import (
    partner_handoff,
    redact_students,
    result_hash,
    run_evidence,
)
from mars777_cop_thief.bonus.bonus_report import build_bonus_game_report
from mars777_cop_thief.game.models import Position
from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

PARTNER = {"group_code": "orcai-mj", "group_slug": "orcai_mj"}
URLS = {
    "group_a_cop": "https://a-cop/mcp",
    "group_a_thief": "https://a-thief/mcp",
    "group_b_cop": "https://b-cop/mcp",
    "group_b_thief": "https://b-thief/mcp",
}
REPOS = {"ours": "https://github.com/ours", "partner": "https://github.com/partner"}
STUDENTS = {"group_a": [{"name": "Alice", "id": "FAKE-NATIONAL-ID"}], "group_b": [{"name": "Bob"}]}


def _sg(index, winner, scores, move_count, barriers=()):
    return SubGameResult(
        index=index,
        rows=8,
        cols=8,
        winner=winner,
        scores=scores,
        cop_start=Position(0, 0),
        thief_start=Position(7, 7),
        cop_final=Position(3, 3),
        thief_final=Position(4, 4),
        move_count=move_count,
        barriers=[Position(*b) for b in barriers],
        events=[{"ok": True}],
        transcript=[{"message": "hi"}],
    )


def _report():
    set_a = [_sg(0, "cop", {"cop": 20, "thief": 5}, 7)]
    set_b = [_sg(3, "thief", {"cop": 5, "thief": 10}, 25)]
    return build_bonus_game_report(
        set_a,
        set_b,
        [None],
        [None],
        partner=PARTNER,
        urls=URLS,
        repos=REPOS,
        students=STUDENTS,
        generated_at_iso="2026-06-25T12:00:00+03:00",
    )


def test_report_is_valid_and_shaped():
    report = _report()
    assert report["report_type"] == "bonus_game" and report["validation_status"] == "valid"
    assert report["official_rules"]["board_size"] == [8, 8]
    assert report["timezone"] == "Asia/Jerusalem"
    assert report["mutual_agreement"] is False
    assert report["partner_confirmation_status"] == "pending"
    assert report["bonus_claim"] is False
    assert [s["pairing"] for s in report["sub_games"]] == ["A", "B"]
    assert report["sub_games"][0]["cop_group"] == "MaRs-777"
    assert report["sub_games"][1]["cop_group"] == "orcai-mj"
    assert set(report["mcp_urls"]) == set(URLS)


def test_totals_by_group():
    totals = _report()["totals_by_group"]
    assert totals["MaRs-777"] == {"score": 30, "wins": 2, "as_cop_score": 20, "as_thief_score": 10}
    assert totals["orcai-mj"] == {"score": 10, "wins": 0, "as_cop_score": 5, "as_thief_score": 5}


def test_result_hash_is_identity_independent_but_outcome_sensitive():
    report = _report()
    h = result_hash(report)
    assert result_hash(redact_students(report)) == h  # redacting IDs must not change the hash
    changed = _report()
    changed["sub_games"][0]["cop_score"] = 5
    assert result_hash(changed) != h


def test_redact_students_and_handoff_are_token_and_id_free():
    report = _report()
    handoff = partner_handoff(report)
    assert handoff["bonus_game"]["group_a"]["students"][0]["id"] == "REDACTED"
    assert handoff["for_partner_group"] == "orcai-mj"
    assert handoff["result_hash"] == result_hash(report)
    assert handoff["tokens_recorded"] is False
    assert "FAKE-NATIONAL-ID" not in str(handoff)


def test_run_evidence_flags():
    evidence = run_evidence(_report(), both_directions=True, errors=[None, None])
    assert evidence["official_bonus_game_run"] is True
    assert evidence["num_sub_games"] == 2 and evidence["both_directions_played"] is True
    assert evidence["mutual_agreement"] is False
    assert evidence["live_gmail_sent"] is False and evidence["bonus_email_sent"] is False
    assert evidence["ids_redacted_in_tracked_evidence"] is True


def test_validator_blocks_premature_mutual_agreement():
    report = _report()
    assert validate_bonus_game_report(report) == []
    report["mutual_agreement"] = True
    errors = validate_bonus_game_report(report)
    assert any("mutual_agreement" in e for e in errors)
    report["partner_confirmation_status"] = "confirmed"
    assert validate_bonus_game_report(report) == []


def test_validator_rejects_wrong_report_type():
    errors = validate_bonus_game_report({"report_type": "internal_game"})
    assert any("report_type must be bonus_game" in e for e in errors)


def test_totals_skip_sub_game_with_no_winner():
    set_a = [_sg(0, None, {"cop": 0, "thief": 0}, 4)]
    set_b = [_sg(3, "thief", {"cop": 5, "thief": 10}, 25)]
    report = build_bonus_game_report(
        set_a,
        set_b,
        ["partner_thief_illegal_move:not_one_step"],
        [None],
        partner=PARTNER,
        urls=URLS,
        repos=REPOS,
        students=STUDENTS,
        generated_at_iso="t",
    )
    assert report["sub_games"][0]["winner_group"] is None
    assert report["totals_by_group"]["MaRs-777"]["wins"] == 1  # only the Set B thief win counts
