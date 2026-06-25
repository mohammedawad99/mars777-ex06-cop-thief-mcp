"""Stable schema constants for the official reports (data only, no behaviour).

Defines the required field sets for the internal and bonus reports, the
token-like patterns that must never appear in a report, and normalized
placeholders used for deterministic evidence artifacts.
"""

from __future__ import annotations

SCHEMA_VERSION = "1.0"
INTERNAL_REPORT_TYPE = "internal_game"
BONUS_REPORT_TYPE = "bonus_game"

INTERNAL_REQUIRED_TOP = (
    "report_type",
    "schema_version",
    "group_code",
    "group_slug",
    "students",
    "github_repo",
    "cop_mcp_url",
    "thief_mcp_url",
    "mcp_status",
    "cloud_status",
    "email_status",
    "timezone",
    "config_summary",
    "sub_games",
    "totals",
    "evidence",
    "generated_at_iso",
    "validation_status",
)

INTERNAL_REQUIRED_SUBGAME = (
    "sub_game_index",
    "board_size",
    "max_moves",
    "start_positions",
    "final_positions",
    "winner",
    "move_count",
    "cop_score",
    "thief_score",
    "barriers",
    "transcript_summary",
    "event_count",
    "outcome_reason",
)

INTERNAL_REQUIRED_TOTALS = (
    "cop_score",
    "thief_score",
    "cop_wins",
    "thief_wins",
    "sub_games_completed",
    "invalid_sub_games",
    "scoring_summary",
)

BONUS_REQUIRED_TOP = (
    "report_type",
    "schema_version",
    "group_a",
    "group_b",
    "github_repos",
    "mcp_urls",
    "timezone",
    "students",
    "sub_games",
    "totals_by_group",
    "bonus_claim",
    "mutual_agreement",
    "agreement_notes",
    "validation_status",
)

# Required top-level keys for a real played bonus_game report (Stage 15D).
BONUS_GAME_REQUIRED_TOP = (
    "report_type",
    "schema_version",
    "group_a",
    "group_b",
    "github_repos",
    "mcp_urls",
    "timezone",
    "official_rules",
    "pairing",
    "sub_games",
    "totals_by_group",
    "bonus_claim",
    "mutual_agreement",
    "partner_confirmation_status",
    "agreement_notes",
    "generated_at_iso",
    "validation_status",
)

# Required keys per played bonus sub-game (pairing-labelled).
BONUS_GAME_REQUIRED_SUBGAME = (
    "sub_game_index",
    "pairing",
    "cop_group",
    "thief_group",
    "board_size",
    "start_positions",
    "final_positions",
    "winner_role",
    "winner_group",
    "move_count",
    "cop_score",
    "thief_score",
    "outcome_reason",
)

# Patterns that must never appear as a report key or string value.
FORBIDDEN_PATTERNS = (
    "auth_token",
    "access_token",
    "refresh_token",
    "secret",
    "password",
    "private_key",
    "cop_mcp_token",
    "thief_mcp_token",
)

# Dummy local tokens must never reach a report either (value-only check).
DUMMY_TOKEN_HINTS = ("dummy-local-cop-token", "dummy-local-thief-token")

# cloud_status values under which local (127.0.0.1) URLs are allowed.
LOCAL_CLOUD_STATUSES = ("not_deployed", "local")

# Normalized placeholders for deterministic, sanitized evidence artifacts.
GENERATED_AT_PLACEHOLDER = "EXAMPLE_GENERATED_AT_UTC"
LOCAL_COP_URL = "http://127.0.0.1:8001/mcp"
LOCAL_THIEF_URL = "http://127.0.0.1:8002/mcp"
DEFAULT_STUDENTS = ({"name": "REPLACE_WITH_STUDENT_NAME", "id": "REPLACE_WITH_STUDENT_ID"},)
