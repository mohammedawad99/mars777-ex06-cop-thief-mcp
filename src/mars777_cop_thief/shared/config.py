"""Safe JSON configuration loading and validation helpers.

Stage 0 only needs to read local default config files and confirm that the
required top-level keys exist. No external services are contacted.
"""

from __future__ import annotations

import json
from pathlib import Path

from mars777_cop_thief.constants import GAME_CONFIG_REQUIRED_KEYS


class ConfigError(ValueError):
    """Raised when a configuration file is missing or structurally invalid."""


def load_json_config(path: str | Path) -> dict:
    """Load a JSON config file and return it as a dict.

    Raises ConfigError if the file is missing or is not a JSON object.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Config root must be an object: {config_path}")
    return data


def validate_game_config(data: dict) -> dict:
    """Validate that the required game-config keys are present.

    Returns the same dict on success; raises ConfigError listing any missing
    keys otherwise.
    """
    missing = [key for key in GAME_CONFIG_REQUIRED_KEYS if key not in data]
    if missing:
        raise ConfigError(f"Missing required game config keys: {', '.join(missing)}")
    return data


def load_game_config(path: str | Path) -> dict:
    """Load and validate the default game configuration in one call."""
    return validate_game_config(load_json_config(path))
