"""Inter-group bonus readiness gate (Stage 15A): intake + compatibility + strategy.

Read-only go/no-go check. Validates our own public-cloud readiness (URLs, local
tokens, local student identities, Gmail OAuth — presence only, never printed),
ingests a LOCAL git-ignored partner file (.secrets/bonus_partner.local.json,
auto-created from a tracked placeholder template if missing), and — only when the
partner endpoints and tokens are real — runs a safe compatibility smoke against the
partner's public Cop/Thief MCP URLs (reusing the deterministic E2E flow). It never
sends Gmail, never runs a full bonus game, and never prints tokens or student IDs.
Writes sanitized, token-free evidence and prints safe flags only.

    MARS777_STUDENTS_FILE=.secrets/students.local.json \
    uv run python scripts/bonus_partner_readiness.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mars777_cop_thief.bonus.intake import is_placeholder, validate_partner
from mars777_cop_thief.gmail.preflight import run_gmail_preflight

_ROOT = Path(__file__).resolve().parents[1]
EVID, SECRETS, CONFIG = _ROOT / "results" / "evidence", _ROOT / ".secrets", _ROOT / "config"
PARTNER_FILE = Path(
    os.environ.get("MARS777_BONUS_PARTNER_FILE", SECRETS / "bonus_partner.local.json")
)
CLOUD_ENV = SECRETS / "cloud-run.local.env"
STUDENTS_FILE = Path(os.environ.get("MARS777_STUDENTS_FILE", SECRETS / "students.local.json"))
COP_URL = "https://mars777-cop-mcp-6lhzzicqha-zf.a.run.app/mcp"
THIEF_URL = "https://mars777-thief-mcp-6lhzzicqha-zf.a.run.app/mcp"


def _self_ready(env) -> tuple[dict, list]:
    cloud = CLOUD_ENV.read_text(encoding="utf-8") if CLOUD_ENV.is_file() else ""
    tokens_ok = "COP_MCP_TOKEN=" in cloud and "THIEF_MCP_TOKEN=" in cloud
    students_ok = (
        STUDENTS_FILE.is_file()
        and len(json.loads(STUDENTS_FILE.read_text(encoding="utf-8")).get("students", [])) >= 2
    )
    urls_ok = COP_URL.startswith("https://") and COP_URL.endswith("/mcp")
    gmail_ok = run_gmail_preflight(env=env)["status"] == "ready"
    checks = {
        "our_urls_ok": urls_ok,
        "cloud_tokens_present": tokens_ok,
        "students_present": students_ok,
        "gmail_oauth_ready": gmail_ok,
    }
    labels = {
        "our_urls_ok": "our public Cop/Thief /mcp URLs not configured",
        "cloud_tokens_present": "local Cloud Run tokens missing (.secrets/cloud-run.local.env)",
        "students_present": "local student identities missing/incomplete",
        "gmail_oauth_ready": "Gmail OAuth not ready",
    }
    return checks, [labels[k] for k, ok in checks.items() if not ok]


def _ensure_partner() -> bool:
    if PARTNER_FILE.exists():
        return False
    SECRETS.mkdir(exist_ok=True)
    PARTNER_FILE.write_text(
        (CONFIG / "bonus_partner.template.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    return True


def _partner_smoke(info: dict, data: dict) -> str:
    """Lightweight live compatibility check against the partner's CONFIRMED contract.

    The partner uses setup/observe/my_move/state (NOT our own tool names), so this
    verifies their tool set, per-server role identity, and thief-first turn order via
    the adapter. The deep per-tool warm-up smoke lives in bonus_partner_live_smoke.py.
    """
    cop_url, thief_url = info["partner_cop_mcp_url"], info["partner_thief_mcp_url"]
    cop_tok, thief_tok = data.get("partner_cop_token"), data.get("partner_thief_token")
    if not (
        cop_url and thief_url and not is_placeholder(cop_tok) and not is_placeholder(thief_tok)
    ):
        return "unknown"
    from fastmcp import Client

    from mars777_cop_thief.bonus.partner_adapter import setup_args, supported_contract
    from mars777_cop_thief.mcp_client.client import wait_ready

    async def _go() -> bool:
        if not (await wait_ready(cop_url) and await wait_ready(thief_url)):
            return False
        async with Client(cop_url) as cop, Client(thief_url) as thief:
            if not (
                supported_contract([t.name for t in await cop.list_tools()])
                and supported_contract([t.name for t in await thief.list_tools()])
            ):
                return False
            cop_setup = (await cop.call_tool("setup", setup_args("5x5", token=cop_tok))).data
            thief_setup = (await thief.call_tool("setup", setup_args("5x5", token=thief_tok))).data
            return bool(
                cop_setup.get("role") == "cop"
                and thief_setup.get("role") == "thief"
                and cop_setup.get("snapshot", {}).get("turn") == "thief"
            )

    try:
        return "passed" if asyncio.run(_go()) else "failed"
    except Exception:
        return "failed"


def main() -> int:
    created = _ensure_partner()
    self_checks, self_blockers = _self_ready(os.environ)
    data = json.loads(PARTNER_FILE.read_text(encoding="utf-8"))
    intake_present, urls_present, partner, partner_blockers = validate_partner(data)
    blockers = list(self_blockers) + partner_blockers
    smoke = _partner_smoke(partner, data) if urls_present else "unknown"
    if created:
        blockers.append(
            "partner file created as placeholder; fill .secrets/bonus_partner.local.json"
        )
    if smoke != "passed":
        blockers.append(f"partner compatibility smoke not passed (status: {smoke})")
    bonus_ready = bool(not blockers and intake_present and urls_present and smoke == "passed")
    evid = {
        "stage": "15A",
        "artifact": "bonus_readiness",
        "bonus_ready": bonus_ready,
        "self_cloud_ready": not self_blockers,
        "self_checks": self_checks,
        "partner_intake_present": intake_present,
        "partner_urls_present": urls_present,
        "partner_smoke_passed": smoke,
        "partner": partner,
        "our_cop_mcp_url": COP_URL,
        "our_thief_mcp_url": THIEF_URL,
        "strategy": json.loads(
            (CONFIG / "bonus_strategy.default.json").read_text(encoding="utf-8")
        ),
        "blockers": blockers,
        "mutual_agreement_pending": True,
        "live_gmail_sent": False,
        "bonus_game_run": False,
        "token_values_recorded": False,
        "ids_redacted_in_tracked_evidence": True,
    }
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "bonus_readiness.example.json").write_text(
        json.dumps(evid, indent=2) + "\n", encoding="utf-8"
    )
    flags = {
        k: evid[k]
        for k in (
            "bonus_ready",
            "self_cloud_ready",
            "partner_intake_present",
            "partner_urls_present",
            "partner_smoke_passed",
            "mutual_agreement_pending",
            "live_gmail_sent",
            "bonus_game_run",
        )
    }
    print(json.dumps(flags | {"blockers": blockers}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
