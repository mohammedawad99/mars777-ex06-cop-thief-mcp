"""Pure MCP tool adapters: role-safe payloads delegating to domain logic.

No FastMCP, no network, and no game rules of their own — each adapter builds on
the engine / observability / dialogue / agents packages and returns
JSON-serializable data. Protected adapters apply the auth guard first and never
echo the real token. The LLM lives in the future client, not in these adapters.
"""

from __future__ import annotations

from mars777_cop_thief.agents.observed import observed_cop_action, observed_thief_action
from mars777_cop_thief.constants import GROUP_CODE
from mars777_cop_thief.dialogue.messages import compose_message
from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.game.rules import barrier_violation
from mars777_cop_thief.mcp_servers.auth import check_auth
from mars777_cop_thief.mcp_servers.common import (
    STAGE,
    action_to_dict,
    build_state,
    to_position,
)
from mars777_cop_thief.observability.observation import observe
from mars777_cop_thief.shared.version import __version__


def _radius(game_config: dict) -> int:
    return int(game_config.get("visibility_radius", 1))


def role_info(role: PlayerRole) -> dict:
    """Static role/server identity (unprotected)."""
    return {
        "role": role.value,
        "group_code": GROUP_CODE,
        "stage": STAGE,
        "server_kind": f"{role.value}-mcp",
    }


def health(role: PlayerRole) -> dict:
    """Basic server health and version (unprotected)."""
    return {"status": "ok", "role": role.value, "version": __version__}


def observation(
    game_config, role, cop, thief, token_env, auth_token, move_count=0, barriers_placed=0
):
    """Role-safe partial observation (hidden opponent stays None)."""
    denied = check_auth(auth_token, token_env)
    if denied is not None:
        return denied
    state = build_state(game_config, cop, thief, move_count, barriers_placed)
    return observe(state, role, _radius(game_config)).to_dict()


def message(game_config, role, cop, thief, token_env, auth_token, move_count=0, barriers_placed=0):
    """Free natural-language message generated from the role's observation."""
    denied = check_auth(auth_token, token_env)
    if denied is not None:
        return denied
    obs = observe(
        build_state(game_config, cop, thief, move_count, barriers_placed),
        role,
        _radius(game_config),
    )
    return {
        "role": role.value,
        "opponent_visible": obs.opponent_visible,
        "message": compose_message(obs),
    }


def proposed_action(
    game_config, role, cop, thief, token_env, auth_token, move_count=0, barriers_placed=0
):
    """Observation-based proposed action (cop/thief observed policy)."""
    denied = check_auth(auth_token, token_env)
    if denied is not None:
        return denied
    obs = observe(
        build_state(game_config, cop, thief, move_count, barriers_placed),
        role,
        _radius(game_config),
    )
    policy = observed_cop_action if role is PlayerRole.COP else observed_thief_action
    return {"role": role.value, "action": action_to_dict(policy(obs))}


def barrier_candidate(game_config, cop, thief, target, token_env, auth_token, barriers_placed=0):
    """Cop-only: validate a barrier placement against budget and occupancy."""
    denied = check_auth(auth_token, token_env)
    if denied is not None:
        return denied
    rows, cols = game_config["grid_size"]
    max_barriers = int(game_config["max_barriers"])
    if barriers_placed >= max_barriers:
        return {"role": "cop", "valid": False, "reason": "barrier_limit_reached"}
    target_pos = to_position(target)
    occupied = {to_position(cop), to_position(thief)}
    violation = barrier_violation(target_pos, int(rows), int(cols), set(), occupied)
    if violation is not None:
        return {"role": "cop", "valid": False, "reason": violation.value}
    return {
        "role": "cop",
        "valid": True,
        "action": {
            "type": "place_barrier",
            "target": {"row": target_pos.row, "col": target_pos.col},
        },
        "remaining_budget": max_barriers - barriers_placed - 1,
    }
