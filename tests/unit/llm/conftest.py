"""Fixtures for the LLM-agent tests: role-safe observation samples."""

import pytest


@pytest.fixture
def hidden_obs() -> dict:
    return {
        "role": "cop",
        "self_position": {"row": 0, "col": 0},
        "board": {"rows": 5, "cols": 5},
        "move_count": 0,
        "max_moves": 25,
        "opponent_visible": False,
        "opponent_position": None,
        "visible_barriers": [],
        "barrier_budget": 5,
    }


@pytest.fixture
def visible_obs() -> dict:
    return {
        "role": "cop",
        "self_position": {"row": 2, "col": 2},
        "board": {"rows": 5, "cols": 5},
        "move_count": 3,
        "max_moves": 25,
        "opponent_visible": True,
        "opponent_position": {"row": 2, "col": 3},
        "visible_barriers": [],
        "barrier_budget": 5,
    }
