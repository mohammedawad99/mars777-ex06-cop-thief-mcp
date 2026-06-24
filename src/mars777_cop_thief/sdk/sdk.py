"""Minimal Assignment SDK façade.

This is the single entry point that the game engine, agents, MCP servers, and
orchestrator build on. It exposes version/config helpers, a thin engine factory,
and local self-play entrypoints; all logic lives in the ``game``/``agents``/
``orchestration`` packages, not here.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.agents import cop_policy, thief_policy
from mars777_cop_thief.game import GameEngine
from mars777_cop_thief.mcp_client.game_smoke import run_game_smoke
from mars777_cop_thief.orchestration import (
    build_report,
    run_dialogue_full_game,
    run_dialogue_sub_game,
    run_full_game,
    run_sub_game,
)
from mars777_cop_thief.orchestration.results import SubGameResult
from mars777_cop_thief.reporting import build_official_internal_report, validate_internal_report
from mars777_cop_thief.reporting.generate_evidence_pack import generate as generate_evidence
from mars777_cop_thief.shared.config import load_game_config
from mars777_cop_thief.shared.version import __version__


class AssignmentSdk:
    """Stable façade over shared package capabilities."""

    def get_version(self) -> str:
        """Return the package version string."""
        return __version__

    def load_game_config(self, path: str | Path) -> dict:
        """Load and validate the default game configuration from ``path``."""
        return load_game_config(path)

    def create_game_engine(self, path: str | Path) -> GameEngine:
        """Build a :class:`GameEngine` from a validated config file at ``path``."""
        return GameEngine(self.load_game_config(path))

    def run_local_sub_game(
        self,
        path: str | Path,
        cop_start: object | None = None,
        thief_start: object | None = None,
    ) -> SubGameResult:
        """Run one deterministic local self-play sub-game from a config file."""
        engine = self.create_game_engine(path)
        return run_sub_game(engine, cop_policy, thief_policy, 0, cop_start, thief_start)

    def run_local_full_game(self, path: str | Path) -> dict:
        """Run a full local self-play game and return its JSON-ready report."""
        config = self.load_game_config(path)
        engine = GameEngine(config)
        results = run_full_game(engine, config["num_sub_games"], cop_policy, thief_policy)
        return build_report(config, results)

    def run_local_dialogue_sub_game(self, path: str | Path) -> SubGameResult:
        """Run one observed/dialogue sub-game (partial observability) from config."""
        config = self.load_game_config(path)
        engine = GameEngine(config)
        return run_dialogue_sub_game(engine, config.get("visibility_radius", 1))

    def run_local_dialogue_full_game(self, path: str | Path) -> dict:
        """Run a full observed/dialogue game and return its JSON-ready report."""
        config = self.load_game_config(path)
        engine = GameEngine(config)
        radius = config.get("visibility_radius", 1)
        results = run_dialogue_full_game(engine, config["num_sub_games"], radius)
        return build_report(config, results, mode="observed-dialogue")

    def run_local_mcp_sub_game(self) -> dict:
        """Run one MCP-backed sub-game over local HTTP servers; return the report."""
        return run_game_smoke(num_sub_games=1)

    def run_local_mcp_full_game(self) -> dict:
        """Run the full MCP-backed game over local HTTP servers; return the report."""
        return run_game_smoke()

    def validate_internal_report(self, report: dict) -> list[str]:
        """Validate an official internal report; return errors (empty == valid)."""
        return validate_internal_report(report)

    def build_official_internal_report(self, mcp_report: dict, students=None) -> dict:
        """Build a validated official internal report from an MCP-backed report."""
        return build_official_internal_report(mcp_report, students=students)

    def generate_local_evidence_pack(self, directory=None) -> dict:
        """Generate the sanitized local evidence pack; return a status dict."""
        return generate_evidence(directory=directory)
