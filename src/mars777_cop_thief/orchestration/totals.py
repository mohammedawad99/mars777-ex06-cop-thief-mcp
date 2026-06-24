"""Aggregation of per-sub-game scores into full-game totals."""

from __future__ import annotations

from mars777_cop_thief.orchestration.results import SubGameResult


def total_scores(results: list[SubGameResult]) -> dict:
    """Sum cop/thief scores across all sub-games."""
    totals = {"cop": 0, "thief": 0}
    for result in results:
        totals["cop"] += result.scores["cop"]
        totals["thief"] += result.scores["thief"]
    return totals


def win_counts(results: list[SubGameResult]) -> dict:
    """Count sub-game outcomes by winner (``none`` for unresolved)."""
    counts = {"cop": 0, "thief": 0, "none": 0}
    for result in results:
        counts[result.winner or "none"] += 1
    return counts
