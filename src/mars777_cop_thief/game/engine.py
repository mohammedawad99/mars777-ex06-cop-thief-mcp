"""Deterministic, config-driven Cop-and-Thief game engine core.

The engine owns no I/O and contacts no external service. All tunable parameters
come from the supplied config dict; illegal actions return a structured
``ActionResult`` rather than raising.
"""

from __future__ import annotations

from mars777_cop_thief.game.events import build_event
from mars777_cop_thief.game.models import (
    Action,
    ActionResult,
    ActionType,
    PlayerRole,
    Position,
    RuleViolation,
)
from mars777_cop_thief.game.rules import barrier_violation, move_violation
from mars777_cop_thief.game.state import SubGameState

_ROLE_BY_NAME = {"thief": PlayerRole.THIEF, "cop": PlayerRole.COP}


class GameEngine:
    """Applies actions to sub-game state and scores terminal outcomes."""

    def __init__(self, config: dict) -> None:
        rows, cols = config["grid_size"]
        self.rows, self.cols = int(rows), int(cols)
        self.max_moves = int(config["max_moves"])
        self.max_barriers = int(config["max_barriers"])
        self.allow_stay = bool(config["allow_stay"])
        self.scoring = dict(config["scoring"])
        order = config["turn_order"]
        self.turn_order = tuple(_ROLE_BY_NAME[name] for name in order)

    def new_subgame(
        self, cop: Position | None = None, thief: Position | None = None
    ) -> SubGameState:
        """Create a fresh sub-game; players default to opposite corners."""
        return SubGameState(
            rows=self.rows,
            cols=self.cols,
            cop=cop if cop is not None else Position(0, 0),
            thief=thief if thief is not None else Position(self.rows - 1, self.cols - 1),
            max_moves=self.max_moves,
            max_barriers=self.max_barriers,
            turn_order=self.turn_order,
        )

    def apply_action(self, state: SubGameState, action: Action) -> ActionResult:
        """Validate and apply ``action``; advance state only when legal."""
        if state.terminal:
            return self._fail(state, action, RuleViolation.GAME_OVER)
        if action.role is not state.current_role:
            return self._fail(state, action, RuleViolation.WRONG_TURN)
        if action.type is ActionType.PLACE_BARRIER:
            return self._place_barrier(state, action)
        return self._move(state, action)

    def score_state(self, state: SubGameState) -> dict:
        """Return ``{"cop": int, "thief": int}`` for a terminal state."""
        if state.winner is PlayerRole.COP:
            return {"cop": self.scoring["cop_win"], "thief": self.scoring["thief_loss"]}
        if state.winner is PlayerRole.THIEF:
            return {"cop": self.scoring["cop_loss"], "thief": self.scoring["thief_win"]}
        return {"cop": 0, "thief": 0}

    def _move(self, state: SubGameState, action: Action) -> ActionResult:
        origin = state.position_of(action.role)
        violation = move_violation(
            origin, action.target, state.rows, state.cols, state.barriers, self.allow_stay
        )
        if violation is not None:
            return self._fail(state, action, violation)
        if action.role is PlayerRole.COP:
            state.cop = action.target
        else:
            state.thief = action.target
        return self._commit(state, action, captured=state.cop == state.thief)

    def _place_barrier(self, state: SubGameState, action: Action) -> ActionResult:
        if action.role is not PlayerRole.COP:
            return self._fail(state, action, RuleViolation.THIEF_CANNOT_PLACE_BARRIER)
        if state.barriers_placed >= state.max_barriers:
            return self._fail(state, action, RuleViolation.BARRIER_LIMIT_REACHED)
        violation = barrier_violation(
            action.target, state.rows, state.cols, state.barriers, state.occupied()
        )
        if violation is not None:
            return self._fail(state, action, violation)
        state.barriers.add(action.target)
        state.barriers_placed += 1
        return self._commit(state, action, captured=False)

    def _commit(self, state: SubGameState, action: Action, captured: bool) -> ActionResult:
        state.move_count += 1
        if captured:
            state.terminal, state.winner = True, PlayerRole.COP
        elif state.move_count >= state.max_moves:
            state.terminal, state.winner = True, PlayerRole.THIEF
        return self._result(state, action, True, None, captured, state.terminal, state.winner)

    def _fail(self, state: SubGameState, action: Action, violation: RuleViolation) -> ActionResult:
        return self._result(state, action, False, violation, False, False, None)

    @staticmethod
    def _result(
        state: SubGameState,
        action: Action,
        ok: bool,
        violation: RuleViolation | None,
        captured: bool,
        terminal: bool,
        winner: PlayerRole | None,
    ) -> ActionResult:
        event = build_event(action, ok, violation, captured, terminal, winner, state.move_count)
        return ActionResult(
            ok=ok,
            role=action.role,
            action=action.type,
            violation=violation,
            captured=captured,
            terminal=terminal,
            winner=winner,
            event=event,
        )
