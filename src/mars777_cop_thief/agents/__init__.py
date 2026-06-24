"""Deterministic local agents/policies (no external services)."""

from mars777_cop_thief.agents.baseline import (
    cop_policy,
    first_legal_action,
    legal_moves,
    thief_policy,
)
from mars777_cop_thief.agents.observed import (
    observed_cop_action,
    observed_thief_action,
)

__all__ = [
    "cop_policy",
    "first_legal_action",
    "legal_moves",
    "observed_cop_action",
    "observed_thief_action",
    "thief_policy",
]
