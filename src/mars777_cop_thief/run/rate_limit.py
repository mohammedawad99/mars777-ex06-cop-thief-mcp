"""Resource-guard model (documented limits, validated; not runtime-enforced here).

Reads conservative limits from ``config/rate_limits.default.json`` and the output
cap from ``config/runtime.default.json`` so a run can record and validate its
resource budget.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceGuard:
    """Per-run resource limits (requests/concurrency/output cap)."""

    mcp_requests_per_minute: int
    mcp_max_concurrent: int
    llm_max_output_tokens: int

    @classmethod
    def from_configs(cls, rate_limits: dict, runtime: dict) -> ResourceGuard:
        defaults = rate_limits.get("defaults", {})
        return cls(
            mcp_requests_per_minute=int(defaults.get("mcp_requests_per_minute", 60)),
            mcp_max_concurrent=int(defaults.get("mcp_max_concurrent", 4)),
            llm_max_output_tokens=int(runtime.get("provider_max_output_tokens", 120)),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("mcp_requests_per_minute", self.mcp_requests_per_minute),
            ("mcp_max_concurrent", self.mcp_max_concurrent),
            ("llm_max_output_tokens", self.llm_max_output_tokens),
        ):
            if value <= 0:
                errors.append(f"{name} must be > 0")
        return errors
