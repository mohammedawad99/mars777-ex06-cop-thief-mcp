"""Minimal Assignment SDK façade.

This is the single entry point that the future game engine, agents, MCP
servers, and orchestrator will build on. Stage 0 exposes only version and
config helpers; behaviour is intentionally tiny and fully tested.
"""

from __future__ import annotations

from pathlib import Path

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
