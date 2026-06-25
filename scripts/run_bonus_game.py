"""Stage 15D — run the official inter-group bonus game (no Gmail; no tokens printed).

Plays the agreed 6-sub-game match vs partner group 'orcai-mj' over the live MCP
endpoints, autonomously (the referee, not a human, chooses every move): Set A (3) is
MaRs-777 Cop vs orcai-mj Thief; Set B (3) is orcai-mj Cop vs MaRs-777 Thief. Our
``GameEngine`` is the canonical authority (8x8, thief-first, <=25 plies, <=5 cop
barriers). Tokens come from local git-ignored files and are NEVER printed or written.
Writes the canonical bonus_game JSON, a token-free partner handoff (with result_hash),
and sanitized run evidence; sends no Gmail and never sets mutual_agreement.

    set -a; . .secrets/cloud-run.local.env; set +a
    uv run python scripts/run_bonus_game.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastmcp import Client

from mars777_cop_thief.bonus.bonus_handoff import partner_handoff, redact_students, run_evidence
from mars777_cop_thief.bonus.bonus_report import build_bonus_game_report
from mars777_cop_thief.bonus.cross_engine import (
    DEFAULT_COP_START,
    DEFAULT_THIEF_START,
    bonus_engine,
)
from mars777_cop_thief.bonus.referee import run_cross_subgame
from mars777_cop_thief.bonus.sessions import OurSession, PartnerSession
from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.mcp_client.client import wait_ready

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
OUR_COP_URL = os.environ.get("COP_MCP_URL", "https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app/mcp")
OUR_THIEF_URL = os.environ.get(
    "THIEF_MCP_URL", "https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app/mcp"
)
OUR_REPO = "https://github.com/mohammedawad99/mars777-ex06-cop-thief-mcp"
PARTNER_FILE = Path(
    os.environ.get("MARS777_BONUS_PARTNER_FILE", _ROOT / ".secrets" / "bonus_partner.local.json")
)
STUDENTS_FILE = Path(
    os.environ.get("MARS777_STUDENTS_FILE", _ROOT / ".secrets" / "students.local.json")
)


def _load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"required local file missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


async def _subgame(engine, our, partner_conn, our_role, index, starts, attempts=3):
    """One sub-game on fresh connections; replay from setup on a transient drop."""
    our_url, our_tok = our
    p_url, p_tok, p_role = partner_conn
    for attempt in range(attempts):
        try:
            async with Client(our_url) as oc, Client(p_url) as pc:
                return await run_cross_subgame(
                    engine,
                    OurSession(oc, our_tok, our_role),
                    PartnerSession(pc, p_tok, p_role),
                    our_role,
                    index,
                    *starts,
                )
        except Exception:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(3)


async def _direction(engine, our, partner_conn, our_role, base, starts):
    results, errors = [], []
    for offset in range(3):
        res, err = await _subgame(engine, our, partner_conn, our_role, base + offset, starts)
        results.append(res)
        errors.append(err)
    return results, errors


async def _play(partner: dict, starts: tuple) -> tuple:
    engine = bonus_engine()
    o_cop, o_thief = os.environ["COP_MCP_TOKEN"], os.environ["THIEF_MCP_TOKEN"]
    p_cop_url, p_thief_url = partner["partner_cop_mcp_url"], partner["partner_thief_mcp_url"]
    for url in (OUR_COP_URL, OUR_THIEF_URL, p_cop_url, p_thief_url):
        if not await wait_ready(url):
            raise SystemExit("an MCP endpoint is unreachable; aborting (nothing faked)")
    set_a, err_a = await _direction(
        engine,
        (OUR_COP_URL, o_cop),
        (p_thief_url, partner["partner_thief_token"], PlayerRole.THIEF),
        PlayerRole.COP,
        0,
        starts,
    )
    set_b, err_b = await _direction(
        engine,
        (OUR_THIEF_URL, o_thief),
        (p_cop_url, partner["partner_cop_token"], PlayerRole.COP),
        PlayerRole.THIEF,
        3,
        starts,
    )
    return set_a, err_a, set_b, err_b


_SAFE_KEYS = (
    "official_bonus_game_run",
    "board_size",
    "num_sub_games",
    "both_directions_played",
    "totals_by_group",
    "result_hash",
    "validation_status",
    "mutual_agreement",
    "partner_confirmation_status",
    "live_gmail_sent",
)


def _write(name: str, obj: dict) -> None:
    (EVID / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    partner = _load(PARTNER_FILE)
    students = {
        "group_a": _load(STUDENTS_FILE)["students"],
        "group_b": partner.get("partner_students_public") or [],
    }
    set_a, err_a, set_b, err_b = asyncio.run(
        _play(partner, (DEFAULT_COP_START, DEFAULT_THIEF_START))
    )
    report = build_bonus_game_report(
        set_a,
        set_b,
        err_a,
        err_b,
        partner={
            "group_code": partner["partner_group_code"],
            "group_slug": partner.get("partner_group_slug"),
        },
        urls={
            "group_a_cop": OUR_COP_URL,
            "group_a_thief": OUR_THIEF_URL,
            "group_b_cop": partner["partner_cop_mcp_url"],
            "group_b_thief": partner["partner_thief_mcp_url"],
        },
        repos={"ours": OUR_REPO, "partner": partner["partner_github_repo"]},
        students=students,
        generated_at_iso=datetime.now(ZoneInfo("Asia/Jerusalem")).isoformat(),
    )
    both = bool(set_a) and bool(set_b)
    evidence = run_evidence(report, both_directions=both, errors=err_a + err_b)
    EVID.mkdir(parents=True, exist_ok=True)
    _write("bonus_game_report.example.json", redact_students(report))
    _write("bonus_game_partner_handoff.example.json", partner_handoff(report))
    _write("bonus_game_official_run.example.json", evidence)
    print(json.dumps({k: evidence[k] for k in _SAFE_KEYS}, indent=2))  # no tokens, no IDs
    return 0 if report["validation_status"] == "valid" and both else 1


if __name__ == "__main__":
    raise SystemExit(main())
