"""Project-wide constants shared across the future game engine and servers.

Stage 0 keeps these identifiers stable so configuration, documentation, and
tests reference a single source of truth.
"""

GROUP_CODE = "MaRs-777"
GROUP_SLUG = "mars777"

# Required top-level keys expected in config/game.default.json.
GAME_CONFIG_REQUIRED_KEYS = (
    "version",
    "group_code",
    "group_slug",
    "grid_size",
    "max_moves",
    "num_sub_games",
    "scoring",
    "timezone",
)
