"""Prompted MCP-backed game flow: each turn an LLM agent decides the action.

The trusted orchestrator owns authoritative state and the engine remains the only
authority. Per turn it calls ``get_observation``/``compose_message`` over the MCP
client, prompts the agent, parses the action, and applies it — falling back to a
deterministic legal move when parsing fails or the action is illegal. Prompt
summaries, responses, parse status, and token/cost estimates are recorded.
"""

from __future__ import annotations

from mars777_cop_thief.agents.baseline import first_legal_action
from mars777_cop_thief.game.models import Action, PlayerRole
from mars777_cop_thief.game.rules import step_target
from mars777_cop_thief.orchestration.results import SubGameResult, make_event, snapshot


def _opponent(role: PlayerRole) -> PlayerRole:
    return PlayerRole.THIEF if role is PlayerRole.COP else PlayerRole.COP


def _decision_to_action(role, decision, state) -> Action | None:
    if not decision.parsed_ok:
        return None
    # parsed_ok guarantees a canonical direction, so step_target is never None.
    target = step_target(state.position_of(role), decision.direction)
    if decision.action_type == "barrier":
        return Action.barrier(target)
    return Action.move(role, target, decision.direction)


def _apply(engine, state, role, action, events) -> bool:
    """Apply ``action``; return True if a legal fallback was used instead."""
    before = snapshot(state)
    if action is not None:
        result = engine.apply_action(state, action)
        events.append(make_event(len(events), role, action, result, before, snapshot(state)))
        if result.ok:
            return False
    fallback = first_legal_action(state, role)
    if fallback is None:
        state.terminal = True
        state.winner = PlayerRole.THIEF
        if action is None:
            events.append(make_event(len(events), role, None, None, before, snapshot(state)))
        return True
    fb_before = snapshot(state)
    result = engine.apply_action(state, fallback)
    events.append(make_event(len(events), role, fallback, result, fb_before, snapshot(state)))
    return True


def _entry(index, role, decision, message, observation, fallback_used, leaked) -> dict:
    return {
        "turn_index": index,
        "sender": role.value,
        "recipient": _opponent(role).value,
        "message": message,
        "opponent_visible": observation.get("opponent_visible"),
        "prompt_summary": decision.prompt_summary,
        "llm_response": decision.response_text,
        "parsed_action": {"type": decision.action_type, "direction": decision.direction},
        "parse_ok": decision.parsed_ok,
        "parse_error": decision.parse_error,
        "prompt_tokens_estimate": decision.prompt_tokens_estimate,
        "response_tokens_estimate": decision.response_tokens_estimate,
        "estimated_cost_usd": decision.estimated_cost_usd,
        "fallback_used": fallback_used,
        "audit": {"leaked": leaked},
    }


async def _prompted_turn(engine, state, client, token, agent, transcript, events, acc) -> None:
    role = state.current_role
    args = {
        "cop": [state.cop.row, state.cop.col],
        "thief": [state.thief.row, state.thief.col],
        "auth_token": token,
        "move_count": state.move_count,
        "barriers_placed": state.barriers_placed,
    }
    observation = (await client.call_tool("get_observation", args)).data
    leaked = observation.get("opponent_visible") is False and observation.get("opponent_position")
    message = (await client.call_tool("compose_message", args)).data.get("message")
    decision = agent.decide(observation, message, role.value)
    acc["prompt_tokens"] += decision.prompt_tokens_estimate
    acc["response_tokens"] += decision.response_tokens_estimate
    acc["cost"] += decision.estimated_cost_usd
    if not decision.parsed_ok:
        acc["parse_failures"] += 1
    fallback_used = _apply(engine, state, role, _decision_to_action(role, decision, state), events)
    if fallback_used:
        acc["fallbacks_used"] += 1
    transcript.append(
        _entry(len(transcript), role, decision, message, observation, fallback_used, bool(leaked))
    )


async def run_prompted_sub_game(
    engine,
    cop_client,
    thief_client,
    agent,
    cop_token,
    thief_token,
    acc,
    index=0,
    cop_start=None,
    thief_start=None,
) -> SubGameResult:
    """Play one prompted sub-game; accumulate token/cost stats into ``acc``."""
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
        await _prompted_turn(engine, state, client, token, agent, transcript, events, acc)
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


def new_accumulator() -> dict:
    """Fresh token/cost/fallback accumulator."""
    return {
        "prompt_tokens": 0,
        "response_tokens": 0,
        "cost": 0.0,
        "parse_failures": 0,
        "fallbacks_used": 0,
    }


async def run_prompted_full_game(
    engine, num_sub_games, cop_client, thief_client, agent, cop_token, thief_token
):
    """Play ``num_sub_games`` prompted sub-games; return (results, accumulator)."""
    acc = new_accumulator()
    results = []
    for index in range(num_sub_games):
        results.append(
            await run_prompted_sub_game(
                engine, cop_client, thief_client, agent, cop_token, thief_token, acc, index=index
            )
        )
    return results, acc
