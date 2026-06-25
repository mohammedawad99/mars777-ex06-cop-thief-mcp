"""Unit tests for finalizing the mutually-agreed bonus_game report (pure, no IO)."""

import hashlib
import json

from mars777_cop_thief.bonus.bonus_handoff import (
    HASH_SUBGAME_FIELDS,
    HASH_TOPLEVEL_FIELDS,
    hash_core,
    result_hash,
)
from mars777_cop_thief.bonus.bonus_report import build_bonus_game_report
from mars777_cop_thief.bonus.finalize import (
    HASH_METHOD,
    agreement_evidence,
    final_handoff,
    finalize_agreement,
)
from mars777_cop_thief.game.models import Position
from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

PARTNER = {"group_code": "orcai-mj", "group_slug": "orcai-mj"}
URLS = {f"group_{g}_{r}": f"https://{g}-{r}/mcp" for g in ("a", "b") for r in ("cop", "thief")}
REPOS = {"ours": "https://github.com/ours", "partner": "https://github.com/partner"}
STUDENTS = {"group_a": [{"name": "Alice", "id": "FAKE-NATIONAL-ID"}], "group_b": [{"name": "Bob"}]}


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


def _played_report():
    a = [_sg(i, "thief", {"cop": 5, "thief": 10}, 25) for i in range(3)]
    b = [_sg(i + 3, "cop", {"cop": 20, "thief": 5}, 14) for i in range(3)]
    return build_bonus_game_report(
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


def test_finalize_sets_agreement_and_preserves_results():
    source = _played_report()
    final = finalize_agreement(source, notes="confirmed in writing")
    assert final["mutual_agreement"] is True
    assert final["partner_confirmation_status"] == "confirmed"
    assert final["bonus_claim"] is True
    assert final["agreement_notes"] == "confirmed in writing"
    assert final["validation_status"] == "valid"
    # result fields untouched
    assert final["sub_games"] == source["sub_games"]
    assert final["totals_by_group"] == source["totals_by_group"]
    assert final["official_rules"] == source["official_rules"]
    # source is not mutated
    assert source["mutual_agreement"] is False


def test_result_hash_unchanged_by_finalization():
    source = _played_report()
    final = finalize_agreement(source, notes="x")
    assert result_hash(final) == result_hash(source)


def test_finalized_report_passes_validator():
    final = finalize_agreement(_played_report(), notes="x")
    assert validate_bonus_game_report(final) == []


def test_final_handoff_is_confirmed_and_id_free():
    final = finalize_agreement(_played_report(), notes="x")
    handoff = final_handoff(final)
    assert handoff["mutual_agreement"] is True
    assert handoff["partner_confirmation_status"] == "confirmed"
    assert handoff["result_hash"] == result_hash(final)
    assert handoff["hash_method"]["algorithm"] == "sha256"
    assert handoff["bonus_game"]["group_a"]["students"][0]["id"] == "REDACTED"
    assert "FAKE-NATIONAL-ID" not in str(handoff)


def test_agreement_evidence_flags_and_hash_method():
    final = finalize_agreement(_played_report(), notes="x")
    evidence = agreement_evidence(final, draft_created=True, draft_subject="Subj")
    assert evidence["mutual_agreement"] is True
    assert evidence["partner_confirmation_status"] == "confirmed"
    assert evidence["bonus_claim"] is True
    assert evidence["gmail_draft_created"] is True
    assert evidence["draft_subject"] == "Subj"
    assert evidence["live_gmail_sent"] is False and evidence["bonus_email_sent"] is False
    assert evidence["ids_redacted_in_tracked_evidence"] is True
    assert (
        evidence["hash_method"]["included_top_level_fields"]
        == HASH_METHOD["included_top_level_fields"]
    )
    assert evidence["totals_by_group"]["orcai-mj"]["score"] == 90


def test_hash_method_is_derived_from_implementation():
    # The documented method must mirror the actual hashing constants, not a hand-list.
    assert HASH_METHOD["algorithm"] == "sha256"
    assert HASH_METHOD["included_top_level_fields"] == list(HASH_TOPLEVEL_FIELDS)
    assert HASH_METHOD["included_sub_game_fields"] == list(HASH_SUBGAME_FIELDS)
    assert HASH_METHOD["canonical_json"]["separators"] == [",", ":"]
    assert any("Gmail draft metadata" in e for e in HASH_METHOD["excluded_fields"])
    assert len(HASH_METHOD["recompute_recipe"]) == 3


def test_documented_recipe_reproduces_the_hash():
    # Follow the published recompute_recipe by hand and match result_hash exactly.
    report = finalize_agreement(_played_report(), notes="x")
    core = {
        "official_rules": report["official_rules"],
        "sub_games": [
            {k: s[k] for k in HASH_METHOD["included_sub_game_fields"]} for s in report["sub_games"]
        ],
        "totals_by_group": report["totals_by_group"],
    }
    blob = json.dumps(core, sort_keys=True, separators=(",", ":"))
    recomputed = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    assert recomputed == result_hash(report)
    assert core == hash_core(report)  # the published core equals the implementation's core
