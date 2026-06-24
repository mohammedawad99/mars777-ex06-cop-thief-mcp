"""Bounded retry/timeout policy and a small, injectable retry helper.

Timeouts and retry bounds come from ``config/runtime.default.json`` rather than
being hardcoded. ``retry_call`` takes an injectable ``sleep`` so tests stay fast.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """Validated retry/timeout bounds for orchestration."""

    max_retries: int
    backoff_seconds: float
    connect_timeout: float
    call_timeout: float
    readiness_timeout: float

    @classmethod
    def from_config(cls, config: dict) -> RetryPolicy:
        return cls(
            max_retries=int(config["max_retries"]),
            backoff_seconds=float(config["backoff_seconds"]),
            connect_timeout=float(config["mcp_connect_timeout_seconds"]),
            call_timeout=float(config["mcp_call_timeout_seconds"]),
            readiness_timeout=float(config["server_readiness_timeout_seconds"]),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.max_retries < 0:
            errors.append("max_retries must be >= 0")
        if self.backoff_seconds < 0:
            errors.append("backoff_seconds must be >= 0")
        for name, value in (
            ("connect_timeout", self.connect_timeout),
            ("call_timeout", self.call_timeout),
            ("readiness_timeout", self.readiness_timeout),
        ):
            if value <= 0:
                errors.append(f"{name} must be > 0")
        return errors


def retry_call(func, policy: RetryPolicy, *, is_transient=lambda exc: True, sleep=time.sleep):
    """Call ``func`` with bounded retries on transient errors; re-raise otherwise."""
    attempt = 0
    while True:
        try:
            return func()
        except Exception as exc:
            if not is_transient(exc) or attempt >= policy.max_retries:
                raise
            sleep(policy.backoff_seconds * (attempt + 1))
            attempt += 1
