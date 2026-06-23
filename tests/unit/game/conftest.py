"""Shared fixtures for game-engine unit tests."""

import pytest

from mars777_cop_thief.game import GameEngine


@pytest.fixture
def make_config():
    """Return a builder for a baseline engine config, with optional overrides."""

    def _build(**overrides) -> dict:
        config = {
            "grid_size": [5, 5],
            "max_moves": 25,
            "max_barriers": 5,
            "allow_stay": False,
            "turn_order": ["thief", "cop"],
            "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
        }
        config.update(overrides)
        return config

    return _build


@pytest.fixture
def engine(make_config) -> GameEngine:
    return GameEngine(make_config())
