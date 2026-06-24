"""MCP-backed game flow: run real sub-games by calling the role servers' tools.

The trusted local orchestrator owns the authoritative ``SubGameState`` and the
engine remains the only authority for legality/capture/scoring. Each turn the
active role's tools are called over a FastMCP client (HTTP for the smoke path,
in-process for tests). A proposed action that is illegal is recorded and replaced
by a deterministic legal fallback — the engine's safety net, not an agent ability.
"""

from __future__ import annotations

from mars777_cop_thief.agents.baseline import first_legal_action
from mars777_cop_thief.dialogue.transcript import make_message_event
from mars777_cop_thief.game.engine import GameEngine
from mars777_cop_thief.game.models import Action, PlayerRole, Position
from mars777_cop_thief.game.state import SubGameState
from mars777_cop_thief.orchestration.results import SubGameResult, make_event, snapshot


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


def _to_action(role: PlayerRole, action_dict: dict | None) -> Action | None:
    if not action_dict:
        return None
    target = action_dict.get("target")
    if target is None:
        return None
    return Action.move(role, Position(target["row"], target["col"]), action_dict.get("direction"))


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


async def _mcp_turn(engine, state, client, token, transcript, events) -> None:
    role = state.current_role
    args = {
        "cop": [state.cop.row, state.cop.col],
        "thief": [state.thief.row, state.thief.col],
        "auth_token": token,
        "move_count": state.move_count,
        "barriers_placed": state.barriers_placed,
    }
    observation = (await client.call_tool("get_observation", args)).data
    visible = observation.get("opponent_visible")
    leaked = visible is False and observation.get("opponent_position") is not None
    message = (await client.call_tool("compose_message", args)).data
    audit = {"opponent_visible": visible, "leaked": leaked}
    transcript.append(
        make_message_event(
            len(transcript), role, _opponent(role), message.get("message"), visible, audit
        )
    )
    proposed = (await client.call_tool("propose_action", args)).data
    _apply(engine, state, role, _to_action(role, proposed.get("action")), events)


async def run_mcp_sub_game(
    engine,
    cop_client,
    thief_client,
    cop_token,
    thief_token,
    index=0,
    cop_start=None,
    thief_start=None,
) -> SubGameResult:
    """Play one sub-game where every turn calls the role's MCP tools."""
    state = engine.new_subgame(cop_start, thief_start)
    cop_origin, thief_origin = state.cop, state.thief
    clients = {
        PlayerRole.COP: (cop_client, cop_token),
        PlayerRole.THIEF: (thief_client, thief_token),
    }
    events: list[dict] = []
    transcript: list[dict] = []
    while not state.terminal:
        client, token = clients[state.current_role]
        await _mcp_turn(engine, state, client, token, transcript, events)
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


async def run_mcp_full_game(
    engine, num_sub_games, cop_client, thief_client, cop_token, thief_token
):
    """Play ``num_sub_games`` MCP-backed sub-games and return the results."""
    results = []
    for index in range(num_sub_games):
        results.append(
            await run_mcp_sub_game(
                engine, cop_client, thief_client, cop_token, thief_token, index=index
            )
        )
    return results
