"""Deterministic local self-play runners over the pure game engine.

Runs a single sub-game or a full game of ``num_sub_games`` using callable
policies. Illegal policy actions are recorded and safely replaced by a
deterministic legal fallback; a fully stuck actor ends the sub-game as a thief
survival (no capture occurred). No external services are involved.
"""

from __future__ import annotations

from collections.abc import Callable

from mars777_cop_thief.agents.baseline import first_legal_action
from mars777_cop_thief.game.engine import GameEngine
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.game.state import SubGameState
from mars777_cop_thief.orchestration.results import SubGameResult, make_event, snapshot

Policy = Callable[[SubGameState], "Action | None"]


def _take_turn(engine: GameEngine, state: SubGameState, policy: Policy) -> dict | None:
    """Apply one turn for the current actor, returning extra fallback events."""
    role = state.current_role
    before = snapshot(state)
    action = policy(state)
    if action is not None:
        result = engine.apply_action(state, action)
        first = make_event(0, role, action, result, before, snapshot(state))
        if result.ok:
            return _single(first)
    else:
        first = make_event(0, role, None, None, before, snapshot(state))
    fallback = first_legal_action(state, role)
    if fallback is None:
        # Stuck actor: no capture occurred, so the thief is deemed to survive.
        state.terminal = True
        state.winner = PlayerRole.THIEF
        return _single(first)
    before_fallback = snapshot(state)
    result = engine.apply_action(state, fallback)
    second = make_event(0, role, fallback, result, before_fallback, snapshot(state))
    return {"events": [first, second]}


def _single(event: dict) -> dict:
    return {"events": [event]}


def run_sub_game(
    engine: GameEngine,
    cop_policy: Policy,
    thief_policy: Policy,
    index: int = 0,
    cop_start: Position | None = None,
    thief_start: Position | None = None,
) -> SubGameResult:
    """Play one sub-game to termination and return its structured result."""
    state = engine.new_subgame(cop_start, thief_start)
    cop_origin, thief_origin = state.cop, state.thief
    policies = {PlayerRole.COP: cop_policy, PlayerRole.THIEF: thief_policy}
    events: list[dict] = []
    while not state.terminal:
        turn = _take_turn(engine, state, policies[state.current_role])
        for event in turn["events"]:
            event["turn_index"] = len(events)
            events.append(event)
    return SubGameResult(
        index=index,
        rows=state.rows,
        cols=state.cols,
        winner=state.winner.value if state.winner else None,
        scores=engine.score_state(state),
        cop_start=cop_origin,
        thief_start=thief_origin,
        cop_final=state.cop,
        thief_final=state.thief,
        move_count=state.move_count,
        barriers=sorted(state.barriers, key=lambda p: (p.row, p.col)),
        events=events,
    )


def run_full_game(
    engine: GameEngine,
    num_sub_games: int,
    cop_policy: Policy,
    thief_policy: Policy,
) -> list[SubGameResult]:
    """Play ``num_sub_games`` sub-games from the engine's start policy."""
    return [run_sub_game(engine, cop_policy, thief_policy, index=i) for i in range(num_sub_games)]
