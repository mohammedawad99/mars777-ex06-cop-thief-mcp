"""Automated cross-group bonus referee — our ``GameEngine`` stays canonical.

In every sub-game one role is played by our deployed MCP server (``OurSession``)
and the other by the partner's server (``PartnerSession``). The referee drives
autonomous thief-first turns, applies every move to the authoritative engine,
mirrors our moves to the partner via ``observe``, and queries the partner's own
moves via ``my_move``. A human never selects a move. Our side keeps the engine's
deterministic legal fallback as a safety net (Stage 7 behaviour); an illegal
partner move is recorded and ends that sub-game rather than being papered over.
"""

from __future__ import annotations

from mars777_cop_thief.agents.baseline import first_legal_action
from mars777_cop_thief.dialogue.transcript import make_message_event
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.orchestration.results import SubGameResult, make_event, snapshot


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


def _cell(pos: Position) -> list[int]:
    return [pos.row, pos.col]


def _apply_ours(engine, state, role, action, events) -> None:
    """Apply our proposed move; fall back to the engine's legal move if needed."""
    before = snapshot(state)
    if action is not None:
        result = engine.apply_action(state, action)
        events.append(make_event(len(events), role, action, result, before, snapshot(state)))
        if result.ok:
            return
    else:
        events.append(make_event(len(events), role, None, None, before, snapshot(state)))
    fallback = first_legal_action(state, role)
    if fallback is None:
        state.terminal, state.winner = True, PlayerRole.THIEF
        return
    fb_before = snapshot(state)
    result = engine.apply_action(state, fallback)
    events.append(make_event(len(events), role, fallback, result, fb_before, snapshot(state)))


async def _our_turn(engine, state, role, our_session, partner_session, partner_role, events, ts):
    target, message = await our_session.propose(state)
    action = Action.move(role, Position(*target)) if target else None
    _apply_ours(engine, state, role, action, events)
    ts.append(make_message_event(len(ts), role, partner_role, message, None, {}))
    if not state.terminal:
        await partner_session.observe(role, _cell(state.position_of(role)))


async def _partner_turn(engine, state, role, partner_session, our_role, events, ts) -> str | None:
    before = snapshot(state)
    target, barrier, message = await partner_session.my_move()
    action = Action.barrier(Position(*barrier)) if barrier else Action.move(role, Position(*target))
    result = engine.apply_action(state, action)
    events.append(make_event(len(events), role, action, result, before, snapshot(state)))
    ts.append(make_message_event(len(ts), role, our_role, message, None, {}))
    if not result.ok:
        why = result.violation.value if result.violation else "unknown"
        return f"partner_{role.value}_illegal_move:{why}"
    return None


def _result(engine, state, index, cop_start, thief_start, events, ts) -> SubGameResult:
    return SubGameResult(
        index=index,
        rows=state.rows,
        cols=state.cols,
        winner=state.winner.value if state.winner else None,
        scores=engine.score_state(state),
        cop_start=Position(*cop_start),
        thief_start=Position(*thief_start),
        cop_final=state.cop,
        thief_final=state.thief,
        move_count=state.move_count,
        barriers=sorted(state.barriers, key=lambda p: (p.row, p.col)),
        events=events,
        transcript=ts,
    )


async def run_cross_subgame(
    engine, our_session, partner_session, our_role, index, cop_start, thief_start
):
    """Play one autonomous cross-group sub-game; return ``(SubGameResult, error|None)``."""
    state = engine.new_subgame(Position(*cop_start), Position(*thief_start))
    await partner_session.setup(cop_start, thief_start)
    partner_role = _opponent(our_role)
    events: list[dict] = []
    ts: list[dict] = []
    error = None
    while not state.terminal and error is None:
        if state.current_role is our_role:
            await _our_turn(
                engine, state, our_role, our_session, partner_session, partner_role, events, ts
            )
        else:
            error = await _partner_turn(
                engine, state, partner_role, partner_session, our_role, events, ts
            )
    return _result(engine, state, index, cop_start, thief_start, events, ts), error


async def run_cross_set(
    engine, our_session, partner_session, our_role, *, count, base_index, cop_start, thief_start
):
    """Play ``count`` sub-games of one pairing direction; return ``(results, errors)``."""
    results, errors = [], []
    for offset in range(count):
        res, err = await run_cross_subgame(
            engine,
            our_session,
            partner_session,
            our_role,
            base_index + offset,
            cop_start,
            thief_start,
        )
        results.append(res)
        errors.append(err)
    return results, errors
