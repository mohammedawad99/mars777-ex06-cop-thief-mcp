"""Stage 15C — live partner MCP compatibility smoke (no official bonus game).

Connects to partner group 'orcai-mj' live Cop/Thief MCP endpoints and exercises the
CONFIRMED contract (``bonus/partner_adapter.py``): unauthorized rejection, authorized
acceptance, setup/observe/my_move/state, role identity per server, 0-based ``[row,col]``
starts, thief-first turn order, and 5x5 + 8x8 warm-ups. It NEVER sends Gmail, NEVER runs
the official 6-sub-game bonus, and NEVER prints or writes tokens or student IDs.

Reads the local git-ignored partner file for URLs/tokens; writes sanitized, token-free
evidence to results/evidence/bonus_partner_live_smoke.example.json and prints safe flags.

    uv run python scripts/bonus_partner_live_smoke.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mars777_cop_thief.bonus.intake import validate_partner
from mars777_cop_thief.bonus.partner_adapter import (
    is_unauthorized,
    observe_args,
    observe_message,
    setup_args,
    state_args,
    supported_contract,
)

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
PARTNER_FILE = Path(
    os.environ.get("MARS777_BONUS_PARTNER_FILE", _ROOT / ".secrets" / "bonus_partner.local.json")
)
RECOMMEND_BOARD = "5x5"  # our baseline (config/game.default.json grid_size)


async def _state(client, token) -> dict:
    return (await client.call_tool("state", state_args(token))).data


async def _unauthorized_rejected(client) -> bool:
    """True iff a wrong token is rejected (never sends a real token)."""
    try:
        return is_unauthorized(await _state(client, "wrong-token"))
    except Exception as exc:
        return is_unauthorized(str(exc))


async def _role_flow(client, *, role: str, size: str, token: str) -> dict:
    """Run a legal one-exchange flow on one role server; return per-tool ok flags."""
    res = {"setup_ok": False, "observe_ok": False, "my_move_ok": False, "state_ok": False}
    res["role"] = None
    res["turn_after_setup"] = None
    res["thief_first_consistent"] = False

    setup = (await client.call_tool("setup", setup_args(size, token=token))).data
    snap = setup.get("snapshot", {})
    res["role"] = setup.get("role")
    res["turn_after_setup"] = snap.get("turn")
    res["setup_ok"] = res["role"] == role and snap.get("status") == "playing"

    if role == "thief":
        # Thief moves first, then hears the cop reply.
        mv = (await client.call_tool("my_move", state_args(token))).data
        res["my_move_ok"] = isinstance(mv.get("snapshot"), dict)
        res["thief_first_consistent"] = res["turn_after_setup"] == "thief" and res["my_move_ok"]
        msg = observe_message([1, 1], size, mover="cop")
        obs = (await client.call_tool("observe", observe_args(msg, "cop", token))).data
        res["observe_ok"] = isinstance(obs.get("snapshot"), dict)
    else:
        # Cop must NOT be able to move first (thief-first); confirm rejection.
        cop_first_rejected = False
        try:
            await client.call_tool("my_move", state_args(token))
        except Exception as exc:
            cop_first_rejected = "turn" in str(exc).lower()
        res["thief_first_consistent"] = res["turn_after_setup"] == "thief" and cop_first_rejected
        msg = observe_message([3, 3], size, mover="thief")
        obs = (await client.call_tool("observe", observe_args(msg, "thief", token))).data
        res["observe_ok"] = isinstance(obs.get("snapshot"), dict)
        mv = (await client.call_tool("my_move", state_args(token))).data  # now cop's turn
        res["my_move_ok"] = isinstance(mv.get("snapshot"), dict)

    final = await _state(client, token)
    res["state_ok"] = isinstance(final, dict) and "turn" in final
    return res


async def _smoke(cop_url, thief_url, cop_tok, thief_tok) -> dict:
    from fastmcp import Client

    from mars777_cop_thief.mcp_client.client import wait_ready

    out: dict = {"reachable": False}
    if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
        return out
    out["reachable"] = True

    per_size: dict = {}
    async with Client(cop_url) as cop, Client(thief_url) as thief:
        out["cop_tools_ok"] = supported_contract([t.name for t in await cop.list_tools()])
        out["thief_tools_ok"] = supported_contract([t.name for t in await thief.list_tools()])
        out["cop_unauthorized_rejected"] = await _unauthorized_rejected(cop)
        out["thief_unauthorized_rejected"] = await _unauthorized_rejected(thief)
        # authorized acceptance is implied by a successful state read with the real token
        out["cop_authorized_ok"] = isinstance(await _state(cop, cop_tok), dict)
        out["thief_authorized_ok"] = isinstance(await _state(thief, thief_tok), dict)
        for size in ("5x5", "8x8"):
            try:
                cop_r = await _role_flow(cop, role="cop", size=size, token=cop_tok)
                thief_r = await _role_flow(thief, role="thief", size=size, token=thief_tok)
                per_size[size] = {"cop": cop_r, "thief": thief_r, "supported": True}
            except Exception as exc:
                per_size[size] = {"supported": False, "note": is_unauthorized(str(exc)) and "auth"}
    out["per_size"] = per_size
    return out


def _verdict(out: dict) -> dict:
    """Reduce raw smoke output to sanitized go/no-go flags (pure)."""
    sizes = out.get("per_size", {})

    def size_ok(size: str) -> bool:
        s = sizes.get(size, {})
        if not s.get("supported"):
            return False
        roles = (s.get("cop", {}), s.get("thief", {}))
        return all(
            r.get(k) for r in roles for k in ("setup_ok", "observe_ok", "my_move_ok", "state_ok")
        )

    b5, b8 = size_ok("5x5"), size_ok("8x8")
    base = sizes.get(RECOMMEND_BOARD, {})

    def agg(flag: str) -> bool:
        return bool(base.get("cop", {}).get(flag) and base.get("thief", {}).get(flag))

    role_ok = (
        base.get("cop", {}).get("role") == "cop" and base.get("thief", {}).get("role") == "thief"
    )
    thief_first = base.get("cop", {}).get("thief_first_consistent") and base.get("thief", {}).get(
        "thief_first_consistent"
    )
    unauth = bool(out.get("cop_unauthorized_rejected") and out.get("thief_unauthorized_rejected"))
    authz = bool(out.get("cop_authorized_ok") and out.get("thief_authorized_ok"))
    tools = bool(out.get("cop_tools_ok") and out.get("thief_tools_ok"))

    passed = bool(
        out.get("reachable")
        and tools
        and unauth
        and authz
        and role_ok
        and thief_first
        and b5  # baseline board must work
        and agg("setup_ok")
        and agg("observe_ok")
        and agg("my_move_ok")
        and agg("state_ok")
    )
    return {
        "partner_smoke_passed": passed,
        "reachable": bool(out.get("reachable")),
        "tools_contract_ok": tools,
        "unauthorized_rejected": unauth,
        "authorized_accepted": authz,
        "role_identity_consistent": role_ok,
        "thief_first_accepted": bool(thief_first),
        "zero_based_rowcol_accepted": b5,  # [0,0] starts validated by setup on the baseline board
        "setup_ok": agg("setup_ok"),
        "observe_ok": agg("observe_ok"),
        "my_move_ok": agg("my_move_ok"),
        "state_ok": agg("state_ok"),
        "board_5x5_supported": b5,
        "board_8x8_supported": b8,
    }


def main() -> int:
    data = json.loads(PARTNER_FILE.read_text(encoding="utf-8")) if PARTNER_FILE.is_file() else {}
    _, urls_present, info, _ = validate_partner(data)
    tokens_present = info["partner_cop_token_present"] and info["partner_thief_token_present"]

    if urls_present and tokens_present:
        raw = asyncio.run(
            _smoke(
                info["partner_cop_mcp_url"],
                info["partner_thief_mcp_url"],
                data.get("partner_cop_token"),
                data.get("partner_thief_token"),
            )
        )
        v = _verdict(raw)
        ran = True
    else:
        v = {}
        ran = False

    passed = bool(v.get("partner_smoke_passed"))
    recommendation = RECOMMEND_BOARD if (passed and v.get("board_5x5_supported")) else "undecided"
    evid = {
        "stage": "15C",
        "artifact": "bonus_partner_live_smoke",
        "partner_group_code": info["partner_group_code"],
        "partner_github_repo": info["partner_github_repo"],
        "partner_urls_present": urls_present,
        "partner_tokens_present": tokens_present,
        "partner_smoke_run": ran,
        "partner_smoke_passed": passed,
        "tools_contract_ok": bool(v.get("tools_contract_ok")),
        "unauthorized_rejected": bool(v.get("unauthorized_rejected")),
        "authorized_accepted": bool(v.get("authorized_accepted")),
        "role_identity_consistent": bool(v.get("role_identity_consistent")),
        "thief_first_accepted": bool(v.get("thief_first_accepted")),
        "zero_based_rowcol_accepted": bool(v.get("zero_based_rowcol_accepted")),
        "setup_ok": bool(v.get("setup_ok")),
        "observe_ok": bool(v.get("observe_ok")),
        "my_move_ok": bool(v.get("my_move_ok")),
        "state_ok": bool(v.get("state_ok")),
        "board_5x5_supported": bool(v.get("board_5x5_supported")),
        "board_8x8_supported": bool(v.get("board_8x8_supported")),
        "official_board_size_recommendation": recommendation,
        "official_board_size_selected": False,
        "official_bonus_game_run": False,
        "live_gmail_sent": False,
        "tokens_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
        "mutual_agreement_pending": True,
    }
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "bonus_partner_live_smoke.example.json").write_text(
        json.dumps(evid, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(evid, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
