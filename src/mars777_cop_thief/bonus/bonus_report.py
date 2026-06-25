"""Build the canonical ``bonus_game`` report from both pairing sets (pure, no IO).

Set A is MaRs-777 Cop vs partner Thief; Set B is partner Cop vs MaRs-777 Thief.
Scores follow the agreed bonus scheme already encoded in ``cross_engine`` (via
``GameEngine.score_state``). The report keeps tokens out entirely (only public
URLs) and is validated with ``validate_bonus_game_report``; ``mutual_agreement``
stays ``False`` and ``partner_confirmation_status`` ``"pending"`` here.
"""

from __future__ import annotations

from mars777_cop_thief.bonus.cross_engine import OFFICIAL_RULES, outcome_reason
from mars777_cop_thief.reporting.schemas import BONUS_REPORT_TYPE, SCHEMA_VERSION
from mars777_cop_thief.reporting.validators import validate_bonus_game_report

OUR_GROUP = {"group_code": "MaRs-777", "group_slug": "mars777"}
_MAX_MOVES = OFFICIAL_RULES["max_moves"]


def _summary(transcript: list[dict]) -> dict:
    return {
        "message_count": len(transcript),
        "first_message": transcript[0]["message"] if transcript else None,
        "last_message": transcript[-1]["message"] if transcript else None,
    }


def _pair(positions: dict, key: str) -> dict:
    return {
        role: [positions[key][role]["row"], positions[key][role]["col"]] for role in positions[key]
    }


def _sub_game(result, pairing: str, cop_group: str, thief_group: str, error) -> dict:
    d = result.to_dict()
    winner = d["winner"]
    winner_group = {"cop": cop_group, "thief": thief_group}.get(winner)
    return {
        "sub_game_index": d["index"],
        "pairing": pairing,
        "cop_group": cop_group,
        "thief_group": thief_group,
        "board_size": [d["board"]["rows"], d["board"]["cols"]],
        "max_moves": _MAX_MOVES,
        "start_positions": _pair(d, "start"),
        "final_positions": _pair(d, "final"),
        "winner_role": winner,
        "winner_group": winner_group,
        "move_count": d["move_count"],
        "cop_score": d["scores"]["cop"],
        "thief_score": d["scores"]["thief"],
        "scores_by_group": {cop_group: d["scores"]["cop"], thief_group: d["scores"]["thief"]},
        "barriers": [[b["row"], b["col"]] for b in d["barriers"]],
        "event_count": len(d["events"]),
        "transcript_summary": _summary(d["transcript"]),
        "outcome_reason": outcome_reason(winner, d["move_count"], _MAX_MOVES),
        "error": error,
    }


def _totals_by_group(sub_games: list[dict], groups) -> dict:
    totals = {g: {"score": 0, "wins": 0, "as_cop_score": 0, "as_thief_score": 0} for g in groups}
    for s in sub_games:
        totals[s["cop_group"]]["score"] += s["cop_score"]
        totals[s["cop_group"]]["as_cop_score"] += s["cop_score"]
        totals[s["thief_group"]]["score"] += s["thief_score"]
        totals[s["thief_group"]]["as_thief_score"] += s["thief_score"]
        if s["winner_group"]:
            totals[s["winner_group"]]["wins"] += 1
    return totals


def build_bonus_game_report(
    set_a, set_b, errors_a, errors_b, *, partner, urls, repos, students, generated_at_iso
):
    """Assemble and validate the canonical bonus_game report (tokens never included)."""
    other = partner["group_code"]
    a = [_sub_game(r, "A", "MaRs-777", other, errors_a[i]) for i, r in enumerate(set_a)]
    b = [_sub_game(r, "B", other, "MaRs-777", errors_b[i]) for i, r in enumerate(set_b)]
    sub_games = a + b
    report = {
        "report_type": BONUS_REPORT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "group_a": {**OUR_GROUP, "students": list(students["group_a"])},
        "group_b": {
            "group_code": other,
            "group_slug": partner.get("group_slug"),
            "students": list(students["group_b"]),
        },
        "github_repos": {"MaRs-777": repos["ours"], other: repos["partner"]},
        "mcp_urls": dict(urls),
        "timezone": "Asia/Jerusalem",
        "official_rules": OFFICIAL_RULES,
        "pairing": {
            "set_a": f"MaRs-777 Cop vs {other} Thief",
            "set_b": f"{other} Cop vs MaRs-777 Thief",
        },
        "sub_games": sub_games,
        "totals_by_group": _totals_by_group(sub_games, ("MaRs-777", other)),
        "bonus_claim": False,
        "mutual_agreement": False,
        "partner_confirmation_status": "pending",
        "agreement_notes": (
            "Official 6-sub-game bonus game played autonomously by the MCP agents; "
            "awaiting partner confirmation that the canonical result matches before "
            "mutual_agreement is set."
        ),
        "generated_at_iso": generated_at_iso,
        "validation_status": "pending",
    }
    report["validation_status"] = "valid" if not validate_bonus_game_report(report) else "invalid"
    return report
