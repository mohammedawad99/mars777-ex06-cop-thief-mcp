"""JSON-serializable report for an MCP-backed local game.

Builds on the Stage 3 report (group/config/sub_games/totals) and adds explicit
local MCP status fields. It states **local** status only — no cloud/public
deployment and no email sending are claimed here.
"""

from __future__ import annotations

from mars777_cop_thief.orchestration.report import build_report
from mars777_cop_thief.orchestration.results import SubGameResult


def _any_leak(results: list[SubGameResult]) -> bool:
    """True if any transcript flagged a leaked hidden opponent coordinate."""
    return any(
        event.get("audit", {}).get("leaked") for result in results for event in result.transcript
    )


def build_mcp_report(
    config: dict, results: list[SubGameResult], cop_url: str, thief_url: str
) -> dict:
    """Assemble the MCP-backed game report with local status fields."""
    report = build_report(config, results, mode="mcp-backed")
    report.update(
        {
            "transport": "local_mcp_http",
            "mcp_status": "local_verified",
            "cop_mcp_url": cop_url,
            "thief_mcp_url": thief_url,
            "cloud_status": "not_deployed",
            "email_status": "not_sent",
            "hidden_state_respected": not _any_leak(results),
        }
    )
    return report


def build_prompted_report(
    config, results, accumulator, cop_url, thief_url, provider_name, model_name
) -> dict:
    """MCP-backed report plus fake-local LLM mode and token/cost accounting."""
    report = build_mcp_report(config, results, cop_url, thief_url)
    report.update(
        {
            "mode": "mcp-backed-prompted",
            "llm_mode": "fake_local",
            "provider_name": provider_name,
            "model_name": model_name,
            "total_prompt_tokens_estimate": accumulator["prompt_tokens"],
            "total_response_tokens_estimate": accumulator["response_tokens"],
            "estimated_cost_usd": round(accumulator["cost"], 6),
            "parse_failures": accumulator["parse_failures"],
            "fallbacks_used": accumulator["fallbacks_used"],
            "cost_model": {"rate_per_1k_usd": 0.0, "note": "fake_local: no real spend"},
        }
    )
    return report
