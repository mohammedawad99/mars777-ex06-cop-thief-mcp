"""Shared fixtures for unit tests (full config incl. report fields)."""

import pytest

from mars777_cop_thief.game import GameEngine


@pytest.fixture
def make_config():
    """Return a builder for a full local config, with optional overrides."""

    def _build(**overrides) -> dict:
        config = {
            "version": "1.00",
            "group_code": "MaRs-777",
            "group_slug": "mars777",
            "github_repo": "REPLACE_WITH_GITHUB_REPO_URL",
            "grid_size": [5, 5],
            "max_moves": 25,
            "num_sub_games": 6,
            "max_barriers": 5,
            "allow_stay": False,
            "turn_order": ["thief", "cop"],
            "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
            "timezone": "Asia/Jerusalem",
        }
        config.update(overrides)
        return config

    return _build


@pytest.fixture
def engine(make_config) -> GameEngine:
    return GameEngine(make_config())
