"""Local self-play orchestration (runners, totals, in-memory report builder)."""

from mars777_cop_thief.orchestration.report import build_report
from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.orchestration.runner import run_full_game, run_sub_game
from mars777_cop_thief.orchestration.totals import total_scores, win_counts

__all__ = [
    "SubGameResult",
    "build_report",
    "run_full_game",
    "run_sub_game",
    "total_scores",
    "win_counts",
]
