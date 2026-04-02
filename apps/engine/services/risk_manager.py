import os
from core.config import settings
from core.logger import logger

class RiskManager:
    def __init__(self):
        # Configuration
        self.stop_loss_pct = float(os.getenv("STOP_LOSS_PCT", "0.02")) # 2% stop loss
        self.take_profit_pct = float(os.getenv("TAKE_PROFIT_PCT", "0.04")) # 4% take profit
        self.trailing_stop_pct = float(os.getenv("TRAILING_STOP_PCT", "0.01")) # 1% trailing stop
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE", "0.01")) # 1% risk per trade
        self.binance_fee = 0.001 # 0.1% fee

    def should_exit(self, position, current_price: float) -> str | None:
        """Check if Stop-Loss, Take-Profit, or Trailing-Stop thresholds are hit."""
        side = position.side
        entry_price = position.entry_price

        if side == "BUY":
            # Update max price for trailing stop
            if current_price > position.max_price:
                position.max_price = current_price
            
            # Initial Stop Loss check
            if current_price <= entry_price * (1 - self.stop_loss_pct):
                return "STOP_LOSS"
            
            # Trailing Stop check
            if current_price <= position.max_price * (1 - self.trailing_stop_pct):
                return "TRAILING_STOP"
                
            # Take Profit check
            if current_price >= entry_price * (1 + self.take_profit_pct):
                return "TAKE_PROFIT"
        else:
            # Short position - update "min_price" (stored in max_price field)
            if position.max_price == 0 or current_price < position.max_price:
                position.max_price = current_price
            
            if current_price >= entry_price * (1 + self.stop_loss_pct):
                return "STOP_LOSS"
            
            if current_price >= position.max_price * (1 + self.trailing_stop_pct):
                return "TRAILING_STOP"
                
            if current_price <= entry_price * (1 - self.take_profit_pct):
                return "TAKE_PROFIT"
        
        return None

    def calculate_position_size(self, balance: float, current_price: float) -> float:
        """Calculate position size based on risk per trade."""
        risk_amount = balance * self.risk_per_trade
        # Basic sizing: how much of the asset can we buy with the risked amount?
        size = risk_amount / (current_price * self.stop_loss_pct)

        # Phase 9: Safe Mode Cap
        if settings.binance_mode == "live":
            max_size = settings.real_capital_limit / current_price
            if size > max_size:
                logger.info(f"CAP TRIGGERED: Limiting size {size} to {max_size} ($50 safety cap)")
                size = max_size
        
        return round(size, 4)

# Singleton instance
risk_manager = RiskManager()
