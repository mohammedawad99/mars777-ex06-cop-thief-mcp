"""Partner interop adapter readiness + smoke (Stage 15B) — no official bonus game.

Read-only prep for the inter-group match against partner group 'orcai-mj'. Uses the
pure adapter (bonus/partner_adapter.py) for the partner's setup/observe/my_move/state
contract. When the local git-ignored partner file still lacks real URLs/tokens it
runs in READINESS mode and reports blockers cleanly; once populated, the SAME script
runs an unauthorized smoke, an authorized role/tool compatibility check, and warm-ups
on 5x5 and 8x8 — never printing secrets. It never sends Gmail and never runs the
official 6-sub-game bonus game.

    uv run python scripts/bonus_interop_smoke.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mars777_cop_thief.bonus.intake import validate_partner
from mars777_cop_thief.bonus.partner_adapter import (
    BOARD_SIZES,
    PARTNER_TOOLS,
    is_unauthorized,
    state_args,
    supported_contract,
    warmup_plan,
)

_ROOT = Path(__file__).resolve().parents[1]
EVID = _ROOT / "results" / "evidence"
PARTNER_FILE = Path(
    os.environ.get("MARS777_BONUS_PARTNER_FILE", _ROOT / ".secrets" / "bonus_partner.local.json")
)


async def _live(cop_url, thief_url, cop_tok, thief_tok) -> dict:
    """Run unauthorized + authorized warm-up smokes against the partner (live)."""
    from fastmcp import Client

    from mars777_cop_thief.mcp_client.client import wait_ready

    out = {
        "reachable": False,
        "tools_ok": False,
        "unauthorized": "unknown",
        "warmup_5x5": "unknown",
        "warmup_8x8": "unknown",
    }
    if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
        return out
    out["reachable"] = True
    async with Client(cop_url) as cop:
        out["tools_ok"] = supported_contract([t.name for t in await cop.list_tools()])
        try:
            denied = (await cop.call_tool("state", state_args("wrong-token"))).data
            out["unauthorized"] = "rejected" if is_unauthorized(denied) else "open"
        except Exception as exc:  # partner raises a tool error on a bad token
            out["unauthorized"] = "rejected" if is_unauthorized(str(exc)) else "open"
        for key, size in (("warmup_5x5", "5x5"), ("warmup_8x8", "8x8")):
            try:
                for tool, args in warmup_plan(size, role="cop", token=cop_tok):
                    await cop.call_tool(tool, args)
                out[key] = "passed"
            except Exception:
                out[key] = "failed"
    return out


def main() -> int:
    data = json.loads(PARTNER_FILE.read_text(encoding="utf-8")) if PARTNER_FILE.is_file() else {}
    _, urls_present, info, _ = validate_partner(data)
    tokens_present = info["partner_cop_token_present"] and info["partner_thief_token_present"]
    blockers = []
    if not urls_present:
        blockers.append("partner public Cop/Thief /mcp URLs not yet provided")
    if not tokens_present:
        blockers.append("partner tokens not yet provided")
    blockers.append("official board size (5x5 vs 8x8) not frozen")
    if urls_present and tokens_present:
        live = asyncio.run(
            _live(
                info["partner_cop_mcp_url"],
                info["partner_thief_mcp_url"],
                data.get("partner_cop_token"),
                data.get("partner_thief_token"),
            )
        )
        status = "passed" if live["tools_ok"] and live["warmup_5x5"] == "passed" else "failed"
        if status != "passed":
            blockers.append("partner arg schemas unconfirmed; live interop smoke did not pass")
    else:
        live, status = {}, "unknown"
        blockers.append(
            "partner INTEROP doc not publicly reachable; confirm arg schemas on live endpoints"
        )
    evid = {
        "stage": "15B",
        "artifact": "bonus_interop_readiness",
        "partner_group_code": "orcai-mj",
        "adapter_ready": True,
        "partner_contract_supported": True,
        "supported_partner_tools": list(PARTNER_TOOLS),
        "supported_board_sizes": list(BOARD_SIZES),
        "official_board_size_selected": False,
        "partner_urls_present": urls_present,
        "partner_tokens_present": tokens_present,
        "partner_smoke_status": status,
        "live_checks": live,
        "bonus_game_run": False,
        "live_gmail_sent": False,
        "token_values_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
        "blockers": blockers,
    }
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "bonus_interop_readiness.example.json").write_text(
        json.dumps(evid, indent=2) + "\n", encoding="utf-8"
    )
    safe = {
        k: evid[k]
        for k in (
            "adapter_ready",
            "partner_contract_supported",
            "official_board_size_selected",
            "partner_urls_present",
            "partner_tokens_present",
            "partner_smoke_status",
            "bonus_game_run",
            "live_gmail_sent",
        )
    }
    print(json.dumps(safe | {"blockers": blockers}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
