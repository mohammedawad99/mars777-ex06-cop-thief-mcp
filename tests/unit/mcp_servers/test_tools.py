"""Unit tests for the pure MCP tool adapters (no network)."""

import json

from mars777_cop_thief.constants import GROUP_CODE
from mars777_cop_thief.game.models import PlayerRole
from mars777_cop_thief.mcp_servers import tools

ENV = "COP_MCP_TOKEN"
TOKEN = "local-secret"


def test_role_info_reports_identity():
    info = tools.role_info(PlayerRole.COP)
    assert info["role"] == "cop"
    assert info["group_code"] == GROUP_CODE
    assert info["stage"] == "local-mcp"
    assert info["server_kind"] == "cop-mcp"


def test_health_reports_version():
    health = tools.health(PlayerRole.THIEF)
    assert health["status"] == "ok"
    assert health["role"] == "thief"
    assert health["version"]


def test_observation_requires_valid_token(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.observation(make_config(), PlayerRole.COP, [0, 0], [4, 4], ENV, "bad")
    assert result["error"] == "unauthorized"


def test_cop_observation_hides_thief(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.observation(make_config(), PlayerRole.COP, [0, 0], [4, 4], ENV, TOKEN)
    assert result["opponent_visible"] is False
    assert result["opponent_position"] is None
    assert '"row": 4' not in json.dumps(result)


def test_thief_observation_hides_cop(make_config, monkeypatch):
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    result = tools.observation(
        make_config(), PlayerRole.THIEF, [4, 4], [0, 0], "THIEF_MCP_TOKEN", TOKEN
    )
    assert result["opponent_visible"] is False
    assert result["opponent_position"] is None


def test_message_is_plain_text(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.message(make_config(), PlayerRole.COP, [0, 0], [4, 4], ENV, TOKEN)
    assert isinstance(result["message"], str)
    assert not result["message"].lstrip().startswith(("{", "["))


def test_propose_action_uses_observed_policy(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    # Thief hidden (distance 4): cop must patrol toward centre (1,1), not cheat.
    result = tools.proposed_action(make_config(), PlayerRole.COP, [0, 0], [0, 4], ENV, TOKEN)
    assert result["action"]["type"] == "move"
    assert result["action"]["target"] == {"row": 1, "col": 1}


def test_propose_action_thief_uses_observed_policy(make_config, monkeypatch):
    monkeypatch.setenv("THIEF_MCP_TOKEN", TOKEN)
    result = tools.proposed_action(
        make_config(), PlayerRole.THIEF, [2, 2], [2, 3], "THIEF_MCP_TOKEN", TOKEN
    )
    assert result["action"]["type"] == "move"


def test_propose_action_none_when_stuck(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.proposed_action(
        make_config(grid_size=[1, 1]), PlayerRole.COP, [0, 0], [0, 0], ENV, TOKEN
    )
    assert result["action"] is None


def test_barrier_candidate_respects_budget(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    cfg = make_config()
    full = tools.barrier_candidate(cfg, [0, 0], [4, 4], [2, 2], ENV, TOKEN, barriers_placed=5)
    assert full["valid"] is False
    assert full["reason"] == "barrier_limit_reached"


def test_barrier_candidate_rejects_occupied_cell(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.barrier_candidate(make_config(), [0, 0], [4, 4], [0, 0], ENV, TOKEN)
    assert result["valid"] is False
    assert result["reason"] == "barrier_on_occupied"


def test_barrier_candidate_valid(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    result = tools.barrier_candidate(make_config(), [0, 0], [4, 4], [2, 2], ENV, TOKEN)
    assert result["valid"] is True
    assert result["action"]["type"] == "place_barrier"
    assert result["remaining_budget"] == 4


def test_protected_tools_reject_bad_token(make_config, monkeypatch):
    monkeypatch.setenv(ENV, TOKEN)
    cfg = make_config()
    assert tools.message(cfg, PlayerRole.COP, [0, 0], [4, 4], ENV, "bad")["error"] == "unauthorized"
    assert (
        tools.proposed_action(cfg, PlayerRole.COP, [0, 0], [4, 4], ENV, "bad")["error"]
        == "unauthorized"
    )
    assert (
        tools.barrier_candidate(cfg, [0, 0], [4, 4], [2, 2], ENV, "bad")["error"] == "unauthorized"
    )
