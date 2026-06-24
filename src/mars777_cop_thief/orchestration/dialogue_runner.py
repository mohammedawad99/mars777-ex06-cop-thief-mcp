"""Local observed/dialogue self-play runner.

Each turn the active role builds a partial Observation, speaks a free
natural-language message (recorded in the transcript), then acts from that
observation only. The trusted engine still enforces legality; a pre-chosen
illegal/``None`` action falls back to a legal move — that fallback is a full-state
safety net of the runner, not an agent capability.
"""

from __future__ import annotations

from collections.abc import Callable

from mars777_cop_thief.agents.baseline import first_legal_action
from mars777_cop_thief.agents.observed import observed_cop_action, observed_thief_action
from mars777_cop_thief.dialogue.messages import compose_message
from mars777_cop_thief.dialogue.transcript import audit_facts, make_message_event
from mars777_cop_thief.game.engine import GameEngine
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.game.state import SubGameState
from mars777_cop_thief.observability.observation import Observation, observe
from mars777_cop_thief.orchestration.results import SubGameResult, make_event, snapshot

ObservedPolicy = Callable[[Observation], "Action | None"]


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


def _apply(
    engine: GameEngine,
    state: SubGameState,
    role: PlayerRole,
    action: Action | None,
    events: list[dict],
) -> None:
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
        state.terminal = True
        state.winner = PlayerRole.THIEF
        return
    fb_before = snapshot(state)
    result = engine.apply_action(state, fallback)
    events.append(make_event(len(events), role, fallback, result, fb_before, snapshot(state)))


def run_dialogue_sub_game(
    engine: GameEngine,
    radius: int,
    index: int = 0,
    cop_start: Position | None = None,
    thief_start: Position | None = None,
    cop_policy: ObservedPolicy = observed_cop_action,
    thief_policy: ObservedPolicy = observed_thief_action,
) -> SubGameResult:
    """Play one observed/dialogue sub-game to termination."""
    state = engine.new_subgame(cop_start, thief_start)
    cop_origin, thief_origin = state.cop, state.thief
    policies = {PlayerRole.COP: cop_policy, PlayerRole.THIEF: thief_policy}
    events: list[dict] = []
    transcript: list[dict] = []
    while not state.terminal:
        role = state.current_role
        obs = observe(state, role, radius)
        text = compose_message(obs)
        transcript.append(
            make_message_event(
                len(transcript), role, _opponent(role), text, obs.opponent_visible, audit_facts(obs)
            )
        )
        _apply(engine, state, role, policies[role](obs), events)
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
        transcript=transcript,
    )


def run_dialogue_full_game(
    engine: GameEngine, num_sub_games: int, radius: int
) -> list[SubGameResult]:
    """Play ``num_sub_games`` observed/dialogue sub-games."""
    return [run_dialogue_sub_game(engine, radius, index=i) for i in range(num_sub_games)]
