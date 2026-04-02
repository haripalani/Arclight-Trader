from dataclasses import dataclass
from datetime import datetime
from core.logger import logger, engine_logger

@dataclass
class Position:
    symbol: str
    entry_price: float
    quantity: float
    side: str  # BUY or SELL
    stop_loss: float = 0.0
    take_profit: float = 0.0
    max_price: float = 0.0  # Used for trailing stop
    entry_fee: float = 0.0  # Track fee paid at entry
    opened_at: datetime = None

class PositionTracker:
    def __init__(self):
        self.current_position: Position | None = None

    def open_position(self, symbol: str, price: float, quantity: float, side: str, sl: float = 0, tp: float = 0):
        # Calculate 0.1% Binance fee on entry
        fee = price * quantity * 0.001
        self.current_position = Position(
            symbol=symbol,
            entry_price=price,
            quantity=quantity,
            side=side,
            stop_loss=sl,
            take_profit=tp,
            max_price=price,
            entry_fee=fee,
            opened_at=datetime.now()
        )
        logger.info(f"Position opened: {side} {symbol} @ {price} (Fee paid: ${fee:.4f})")

    def close_position(self):
        self.current_position = None
        logger.info("Position closed.")

    def get_unrealized_pnl(self, current_price: float) -> float:
        if not self.current_position:
            return 0.0
        
        diff = current_price - self.current_position.entry_price
        if self.current_position.side == "SELL":
            diff = -diff
            
        return diff * self.current_position.quantity

    @property
    def is_in_trade(self) -> bool:
        return self.current_position is not None

position_tracker = PositionTracker()
