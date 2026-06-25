"""Unit tests for the partner MCP adapter (pure; no network, no secrets).

The payload keys here mirror the CONFIRMED partner 'orcai-mj' contract discovered
on their live endpoints in Stage 15C (token key ``token``; ``setup`` carries 0-based
``cop``/``thief`` start positions + ``rows``/``cols``/``origin``/``diagonal``;
``observe`` carries ``message``/``mover``; ``my_move`` carries only ``token``).
"""

import pytest

from mars777_cop_thief.bonus.partner_adapter import (
    BOARD_SIZES,
    PARTNER_TOOLS,
    TOKEN_KEY,
    AdapterError,
    board_dims,
    default_starts,
    is_unauthorized,
    my_move_args,
    normalize_cell,
    observe_args,
    observe_message,
    setup_args,
    state_args,
    supported_contract,
    warmup_plan,
)


def test_board_dims_supported_and_rejected():
    assert board_dims("5x5") == (5, 5)
    assert board_dims("8x8") == (8, 8)
    with pytest.raises(AdapterError):
        board_dims("9x9")


def test_normalize_cell_valid_and_out_of_bounds():
    assert normalize_cell([0, 0], "5x5") == [0, 0]
    assert normalize_cell((4, 4), "5x5") == [4, 4]
    assert normalize_cell([7, 7], "8x8") == [7, 7]
    with pytest.raises(AdapterError):
        normalize_cell([5, 0], "5x5")  # row out of bounds on 5x5
    with pytest.raises(AdapterError):
        normalize_cell([0], "5x5")  # not a pair


def test_supported_contract():
    assert supported_contract(["setup", "observe", "my_move", "state", "extra"]) is True
    assert supported_contract(["setup", "observe"]) is False
    assert set(PARTNER_TOOLS) == {"setup", "observe", "my_move", "state"}


def test_default_starts_opposite_corners():
    assert default_starts("5x5") == {"cop": [0, 0], "thief": [4, 4]}
    assert default_starts("8x8") == {"cop": [0, 0], "thief": [7, 7]}


def test_setup_args_real_contract_defaults():
    args = setup_args("8x8", token="T")
    assert TOKEN_KEY == "token"
    assert args["token"] == "T"
    assert args["cop"] == [0, 0]
    assert args["thief"] == [7, 7]
    assert args["rows"] == 8 and args["cols"] == 8
    assert args["origin"] == 0  # 0-based indexing
    assert args["diagonal"] is True
    assert args["max_moves"] == 25
    assert args["max_barriers"] == 5
    assert "role" not in args and "auth_token" not in args  # old provisional keys are gone


def test_setup_args_custom_starts_validated():
    args = setup_args("5x5", token="T", cop_start=[0, 0], thief_start=(3, 2))
    assert args["cop"] == [0, 0] and args["thief"] == [3, 2]
    with pytest.raises(AdapterError):
        setup_args("5x5", token="T", thief_start=[5, 5])  # off-board


def test_observe_message_and_args():
    msg = observe_message([3, 3], "5x5", mover="thief")
    assert "[3, 3]" in msg and "thief" in msg
    assert observe_args(msg, "thief", "T") == {"message": msg, "mover": "thief", "token": "T"}
    with pytest.raises(AdapterError):
        observe_message([9, 9], "5x5", mover="cop")  # off-board


def test_state_and_my_move_args_token_only():
    assert state_args("T") == {"token": "T"}
    assert my_move_args("T") == {"token": "T"}  # partner picks its own move; no move arg


def test_is_unauthorized_detection():
    assert is_unauthorized("Error calling tool 'state': invalid or missing MCP token") is True
    assert is_unauthorized({"error": "unauthorized token"}) is True
    assert is_unauthorized("not cop's turn") is False
    assert is_unauthorized({"status": "playing"}) is False


@pytest.mark.parametrize("size", list(BOARD_SIZES))
@pytest.mark.parametrize("role", ["cop", "thief"])
def test_warmup_plan_touches_full_contract_in_legal_order(size, role):
    plan = warmup_plan(size, role=role, token="T")
    tools = [tool for tool, _ in plan]
    assert tools[0] == "setup" and tools[-1] == "state"
    assert set(tools) == {"setup", "observe", "my_move", "state"}
    if role == "thief":  # thief-first: move, then hear cop's reply
        assert tools.index("my_move") < tools.index("observe")
    else:  # cop: hear thief's move first, then reply
        assert tools.index("observe") < tools.index("my_move")
    for _, args in plan:
        assert args["token"] == "T"
