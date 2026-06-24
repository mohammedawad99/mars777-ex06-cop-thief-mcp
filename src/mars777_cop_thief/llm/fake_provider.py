"""Deterministic, offline fake LLM provider (``llm_mode: fake_local``).

Standard-library only and no network. It reasons over the role-safe observation
exactly like the observed baseline policy (cop pursues a visible thief or patrols
the centre; thief flees a visible cop or explores the edges) and emits a natural
-language line ending in ``ACTION: move <direction>``. It never emits exact
opponent coordinates.
"""

from __future__ import annotations

from mars777_cop_thief.game.models import DIRECTION_DELTAS, Position
from mars777_cop_thief.llm.cost import FAKE_LOCAL_RATE_PER_1K, estimate_cost, estimate_tokens
from mars777_cop_thief.llm.provider import LlmResponse
from mars777_cop_thief.observability.visibility import relative_direction

_CANON = tuple(DIRECTION_DELTAS)


def _cheby(a: dict, b: dict) -> int:
    return max(abs(a["row"] - b["row"]), abs(a["col"] - b["col"]))


def _step(cell: dict, direction: str) -> dict:
    drow, dcol = DIRECTION_DELTAS[direction]
    return {"row": cell["row"] + drow, "col": cell["col"] + dcol}


def _legal_moves(obs: dict) -> list[tuple[str, dict]]:
    me, board = obs["self_position"], obs["board"]
    barriers = {(b["row"], b["col"]) for b in obs.get("visible_barriers", [])}
    moves = []
    for direction in _CANON:
        target = _step(me, direction)
        in_bounds = 0 <= target["row"] < board["rows"] and 0 <= target["col"] < board["cols"]
        if in_bounds and (target["row"], target["col"]) not in barriers:
            moves.append((direction, target))
    return moves


def _choose_direction(role: str, obs: dict) -> str | None:
    moves = _legal_moves(obs)
    if not moves:
        return None
    if obs["opponent_visible"] and obs.get("opponent_position"):
        point = obs["opponent_position"]
    else:
        board = obs["board"]
        point = {"row": (board["rows"] - 1) // 2, "col": (board["cols"] - 1) // 2}
    pick = min if role == "cop" else max
    return pick(moves, key=lambda item: _cheby(item[1], point))[0]


class FakeLocalProvider:
    """Deterministic local provider used for tests and offline runs."""

    provider_name = "fake_local"
    model_name = "deterministic-rule-based-v1"

    def complete(self, prompt: str, *, role: str, context: dict) -> LlmResponse:
        text = self._reason(role, context["observation"])
        prompt_tokens = estimate_tokens(prompt)
        response_tokens = estimate_tokens(text)
        return LlmResponse(
            text=text,
            provider_name=self.provider_name,
            model_name=self.model_name,
            prompt_tokens_estimate=prompt_tokens,
            response_tokens_estimate=response_tokens,
            estimated_cost_usd=estimate_cost(
                prompt_tokens, response_tokens, FAKE_LOCAL_RATE_PER_1K
            ),
            metadata={"llm_mode": "fake_local"},
        )

    def _reason(self, role: str, obs: dict) -> str:
        direction = _choose_direction(role, obs)
        opponent = "thief" if role == "cop" else "cop"
        if direction is None:
            return "I have no legal move available. ACTION: stay"
        if obs["opponent_visible"] and obs.get("opponent_position"):
            me = Position(obs["self_position"]["row"], obs["self_position"]["col"])
            opp = Position(obs["opponent_position"]["row"], obs["opponent_position"]["col"])
            rel = relative_direction(me, opp) or "nearby"
            return (
                f"The {opponent} is visible to the {rel}; I will close in. ACTION: move {direction}"
            )
        return (
            f"I cannot see the {opponent}, so I will explore {direction}. ACTION: move {direction}"
        )
