"""Deterministic local agents/policies (no external services)."""

from mars777_cop_thief.agents.baseline import (
    cop_policy,
    first_legal_action,
    legal_moves,
    thief_policy,
)

__all__ = ["cop_policy", "first_legal_action", "legal_moves", "thief_policy"]
