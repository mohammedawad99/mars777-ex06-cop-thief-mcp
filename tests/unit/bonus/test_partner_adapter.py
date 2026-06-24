"""Unit tests for the partner MCP adapter (pure; no network, no secrets)."""

import pytest

from mars777_cop_thief.bonus.partner_adapter import (
    BOARD_SIZES,
    PARTNER_TOOLS,
    AdapterError,
    board_dims,
    my_move_args,
    normalize_cell,
    observe_args,
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


def test_setup_args_carries_rules_and_token():
    args = setup_args("8x8", role="cop", token="T")
    assert args["auth_token"] == "T"
    assert args["role"] == "cop"
    assert args["board"] == [8, 8]
    assert args["first_player"] == "thief"
    assert args["max_moves"] == 25
    assert args["max_barriers"] == 5
    assert args["coords"] == "0-based [row,col]"


def test_observe_state_my_move_args():
    assert observe_args("T") == {"auth_token": "T"}
    assert state_args("T") == {"auth_token": "T"}
    mv = my_move_args([1, 2], "5x5", token="T")
    assert mv == {"auth_token": "T", "move": [1, 2]}
    with pytest.raises(AdapterError):
        my_move_args([9, 9], "5x5", token="T")


@pytest.mark.parametrize("size", list(BOARD_SIZES))
def test_warmup_plan_orders_full_contract(size):
    plan = warmup_plan(size, role="thief", token="T")
    assert [tool for tool, _ in plan] == ["setup", "observe", "my_move", "state"]
    rows, cols = BOARD_SIZES[size]
    move = dict(plan)["my_move"]["move"]
    assert 0 <= move[0] < rows and 0 <= move[1] < cols
