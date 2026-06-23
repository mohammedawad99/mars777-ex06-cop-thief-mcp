"""Minimal Assignment SDK façade.

This is the single entry point that the game engine, agents, MCP servers, and
orchestrator build on. It exposes version/config helpers and a thin factory for
the game engine; all game logic lives in the ``game`` package, not here.
"""

from __future__ import annotations

from pathlib import Path

from mars777_cop_thief.game import GameEngine
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
