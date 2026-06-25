"""Unit tests for the pure verdict reducer in scripts/bonus_partner_live_smoke.py.

No network: feeds synthetic raw smoke output (the shape produced live against the
partner 'orcai-mj' endpoints in Stage 15C) and checks the go/no-go reduction.
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "bonus_partner_live_smoke.py"


@pytest.fixture(scope="module")
def smoke():
    spec = importlib.util.spec_from_file_location("bonus_partner_live_smoke", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _role(role, **over):
    base = {
        "role": role,
        "turn_after_setup": "thief",
        "thief_first_consistent": True,
        "setup_ok": True,
        "observe_ok": True,
        "my_move_ok": True,
        "state_ok": True,
    }
    base.update(over)
    return base


def _raw(**over):
    raw = {
        "reachable": True,
        "cop_tools_ok": True,
        "thief_tools_ok": True,
        "cop_unauthorized_rejected": True,
        "thief_unauthorized_rejected": True,
        "cop_authorized_ok": True,
        "thief_authorized_ok": True,
        "per_size": {
            "5x5": {"supported": True, "cop": _role("cop"), "thief": _role("thief")},
            "8x8": {"supported": True, "cop": _role("cop"), "thief": _role("thief")},
        },
    }
    raw.update(over)
    return raw


def test_verdict_all_green(smoke):
    v = smoke._verdict(_raw())
    assert v["partner_smoke_passed"] is True
    for k in (
        "tools_contract_ok",
        "unauthorized_rejected",
        "authorized_accepted",
        "role_identity_consistent",
        "thief_first_accepted",
        "zero_based_rowcol_accepted",
        "setup_ok",
        "observe_ok",
        "my_move_ok",
        "state_ok",
        "board_5x5_supported",
        "board_8x8_supported",
    ):
        assert v[k] is True, k


def test_verdict_8x8_unsupported_still_passes_on_baseline(smoke):
    raw = _raw()
    raw["per_size"]["8x8"] = {"supported": False}
    v = smoke._verdict(raw)
    assert v["board_8x8_supported"] is False
    assert v["board_5x5_supported"] is True
    assert v["partner_smoke_passed"] is True  # baseline 5x5 is what gates the verdict


def test_verdict_fails_if_baseline_broken(smoke):
    raw = _raw()
    raw["per_size"]["5x5"]["cop"]["my_move_ok"] = False
    v = smoke._verdict(raw)
    assert v["board_5x5_supported"] is False
    assert v["partner_smoke_passed"] is False


def test_verdict_fails_on_open_auth(smoke):
    v = smoke._verdict(_raw(cop_unauthorized_rejected=False))
    assert v["unauthorized_rejected"] is False
    assert v["partner_smoke_passed"] is False


def test_verdict_fails_on_wrong_role_identity(smoke):
    raw = _raw()
    raw["per_size"]["5x5"]["cop"]["role"] = "thief"
    v = smoke._verdict(raw)
    assert v["role_identity_consistent"] is False
    assert v["partner_smoke_passed"] is False


def test_verdict_unreachable(smoke):
    v = smoke._verdict({"reachable": False, "per_size": {}})
    assert v["partner_smoke_passed"] is False
    assert v["board_5x5_supported"] is False
