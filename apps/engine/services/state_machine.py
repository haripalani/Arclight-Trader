from enum import Enum

class BotState(str, Enum):
    WAITING = "WAITING"
    READY   = "READY"
    TRADING = "TRADING"
    PAUSED  = "PAUSED"

class StateMachine:
    """
    Formal state machine for the trading bot.
    All transitions are explicit and logged.
    No ambiguous states. No shortcuts.
    """
    def __init__(self):
        self._state = BotState.WAITING
        self._history: list[dict] = []

    @property
    def state(self) -> BotState:
        return self._state

    def _transition(self, new_state: BotState, reason: str):
        old = self._state
        self._state = new_state
        entry = {"from": old, "to": new_state, "reason": reason}
        self._history.append(entry)

    def on_good_signal(self):
        if self._state == BotState.WAITING:
            self._transition(BotState.READY, "Score threshold met")

    def on_trade_entered(self):
        if self._state == BotState.READY:
            self._transition(BotState.TRADING, "Trade executed")

    def on_trade_closed(self):
        if self._state == BotState.TRADING:
            self._transition(BotState.WAITING, "Trade closed, scanning again")

    def on_loss_streak(self):
        if self._state in (BotState.TRADING, BotState.WAITING, BotState.READY):
            self._transition(BotState.PAUSED, "3 consecutive losses — paused for protection")

    def on_resume(self):
        if self._state == BotState.PAUSED:
            self._transition(BotState.WAITING, "Bot manually or automatically resumed")

    def on_gate_fail(self):
        if self._state == BotState.READY:
            self._transition(BotState.WAITING, "Gate check failed — signal invalidated")

    def status_dict(self) -> dict:
        return {
            "state": self._state,
            "history": self._history[-5:],  # last 5 transitions
        }

state_machine = StateMachine()
