MAX_CONSECUTIVE_LOSSES = 3

class LossTracker:
    """
    Tracks consecutive losses with zero tolerance.
    3 losses in a row = system pauses. No emotion. No "one more try".
    """
    def __init__(self):
        self._consecutive_losses = 0
        self._total_trades = 0
        self._wins = 0
        self._losses = 0

    def record_win(self):
        self._consecutive_losses = 0  # Reset streak on ANY win
        self._wins += 1
        self._total_trades += 1

    def record_loss(self):
        self._consecutive_losses += 1
        self._losses += 1
        self._total_trades += 1

    @property
    def should_pause(self) -> bool:
        return self._consecutive_losses >= MAX_CONSECUTIVE_LOSSES

    @property
    def consecutive_losses(self) -> int:
        return self._consecutive_losses

    @property
    def win_rate(self) -> float:
        if self._total_trades == 0:
            return 0.0
        return round((self._wins / self._total_trades) * 100, 1)

    def reset(self):
        self._consecutive_losses = 0

    def stats(self) -> dict:
        return {
            "total_trades": self._total_trades,
            "wins": self._wins,
            "losses": self._losses,
            "consecutive_losses": self._consecutive_losses,
            "win_rate": self.win_rate,
            "paused": self.should_pause,
        }

loss_tracker = LossTracker()
