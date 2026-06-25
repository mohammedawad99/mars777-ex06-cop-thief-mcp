"""Referee loop tests with fully scripted fake sessions (deterministic, no network).

The fake partner mirrors the real protocol (tracks its own pieces via setup/
observe and moves one legal step on my_move) so every move applied to the
canonical engine is legal — exactly as the live partner contract guarantees.
"""

import asyncio

from mars777_cop_thief.bonus.cross_engine import bonus_engine
from mars777_cop_thief.bonus.referee import _apply_ours, run_cross_set, run_cross_subgame
from mars777_cop_thief.game.models import Action, PlayerRole, Position


def _step(me, target, rows=8, cols=8):
    dr = (target[0] > me[0]) - (target[0] < me[0])
    dc = (target[1] > me[1]) - (target[1] < me[1])
    nr, nc = me[0] + dr, me[1] + dc
    if (nr, nc) == tuple(me):
        nr = me[0] + 1 if me[0] + 1 < rows else me[0] - 1
    return [max(0, min(rows - 1, nr)), max(0, min(cols - 1, nc))]


class FakeOur:
    """Our side: step one legal cell toward (cop) / away from (thief) the opponent."""

    def __init__(self, propose_none=False):
        self.propose_none = propose_none

    async def propose(self, state):
        if self.propose_none:
            return None, "noop"
        role = state.current_role
        me = (state.position_of(role).row, state.position_of(role).col)
        opp = state.thief if role is PlayerRole.COP else state.cop
        target = (opp.row, opp.col) if role is PlayerRole.COP else (7 - opp.row, 7 - opp.col)
        nr, nc = _step(list(me), target)
        return (nr, nc), "ours"


class FakePartner:
    """Mirrors the partner contract; moves its own piece toward ``target``."""

    def __init__(self, role, target, jump=False, barrier_on=None):
        self.role, self.target, self.jump, self.barrier_on = role, target, jump, barrier_on
        self.cop = self.thief = None
        self.turn = 0

    async def setup(self, cop_start, thief_start):
        self.cop, self.thief = list(cop_start), list(thief_start)
        return self.role.value

    async def observe(self, mover_role, cell):
        if mover_role is PlayerRole.COP:
            self.cop = list(cell)
        else:
            self.thief = list(cell)

    async def my_move(self):
        self.turn += 1
        if self.jump:
            return (5, 5), None, "jump"  # illegal multi-step from a corner start
        if self.barrier_on == self.turn:
            return tuple(self.cop), (3, 3), "wall"
        if self.role is PlayerRole.COP:
            self.cop = _step(self.cop, self.target)
            return tuple(self.cop), None, "pcop"
        self.thief = _step(self.thief, self.target)
        return tuple(self.thief), None, "pthief"


def _run(our, partner, our_role, **kw):
    return asyncio.run(
        run_cross_subgame(bonus_engine(), our, partner, our_role, 0, [0, 0], [7, 7], **kw)
    )


def test_set_a_capture_when_partner_thief_walks_into_cop():
    partner = FakePartner(PlayerRole.THIEF, target=(0, 0))  # thief drifts onto cop at [0,0]
    res, err = asyncio.run(
        run_cross_subgame(bonus_engine(), FakeOur(), partner, PlayerRole.COP, 2, [0, 0], [1, 1])
    )
    assert err is None and res.winner == "cop"
    assert res.scores == {"cop": 20, "thief": 5} and res.rows == 8


def test_set_b_thief_survives_to_max_moves():
    partner = FakePartner(PlayerRole.COP, target=(0, 0))  # cop retreats; never captures
    res, err = _run(FakeOur(), partner, PlayerRole.THIEF)
    assert err is None and res.winner == "thief"
    assert res.move_count == 25 and res.scores == {"cop": 5, "thief": 10}


def test_partner_illegal_move_is_recorded_and_stops():
    partner = FakePartner(PlayerRole.THIEF, target=(0, 0), jump=True)
    res, err = _run(FakeOur(), partner, PlayerRole.COP)
    assert err is not None and "illegal_move" in err
    assert res.winner is None  # game halted, not a real terminal


def test_partner_cop_barrier_is_applied_to_canonical_engine():
    partner = FakePartner(PlayerRole.COP, target=(0, 0), barrier_on=1)
    res, err = _run(FakeOur(), partner, PlayerRole.THIEF)
    assert err is None
    assert {"row": 3, "col": 3} in res.to_dict()["barriers"]


def test_our_none_proposal_uses_engine_fallback():
    partner = FakePartner(PlayerRole.COP, target=(0, 0))
    res, err = _run(FakeOur(propose_none=True), partner, PlayerRole.THIEF)
    assert err is None and res.move_count == 25 and res.events


def test_run_cross_set_runs_n_subgames():
    partner = FakePartner(PlayerRole.THIEF, target=(7, 7))
    results, errors = asyncio.run(
        run_cross_set(
            bonus_engine(),
            FakeOur(),
            partner,
            PlayerRole.COP,
            count=3,
            base_index=0,
            cop_start=[0, 0],
            thief_start=[7, 7],
        )
    )
    assert len(results) == 3 and len(errors) == 3
    assert [r.index for r in results] == [0, 1, 2]


def test_apply_ours_illegal_proposal_falls_back_to_legal_move():
    engine = bonus_engine()
    state = engine.new_subgame(Position(0, 0), Position(7, 7))
    state.move_count = 1  # cop's turn
    events = []
    _apply_ours(engine, state, PlayerRole.COP, Action.move(PlayerRole.COP, Position(5, 5)), events)
    assert len(events) == 2 and state.move_count == 2  # illegal attempt + legal fallback applied


def test_apply_ours_stuck_actor_ends_as_thief_survival():
    engine = bonus_engine()
    state = engine.new_subgame(Position(0, 0), Position(7, 7))
    for cell in [(0, 1), (1, 0), (1, 1)]:  # box the cop into the corner
        state.barriers.add(Position(*cell))
    events = []
    _apply_ours(engine, state, PlayerRole.COP, None, events)
    assert state.terminal and state.winner is PlayerRole.THIEF
