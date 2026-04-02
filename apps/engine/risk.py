import datetime
from core.logger import logger

class RiskManager:
    # Safe Defaults as requested
    MAX_POSITION_SIZE_PCT = 2.0  # max 2% of account balance per trade
    MAX_DAILY_DRAWDOWN_PCT = 5.0  # halt trading if down 5% on the day
    MAX_OPEN_POSITIONS = 3
    STOP_LOSS_PCT = 1.5          # auto stop-loss 1.5% below entry price
    TAKE_PROFIT_PCT = 3.0         # auto take-profit 3.0% above entry price

    def __init__(self):
        self.daily_pnl = 0.0
        self.last_pnl_reset = datetime.datetime.now(datetime.timezone.utc).date()
        self.trading_halted = False
        self.open_positions_count = 0

    def _check_reset_daily(self):
        """Reset PnL at midnight UTC."""
        now = datetime.datetime.now(datetime.timezone.utc).date()
        if now > self.last_pnl_reset:
            logger.info("New day detected (UTC). Resetting daily PnL and clearing halts.")
            self.daily_pnl = 0.0
            self.last_pnl_reset = now
            self.trading_halted = False

    def approve_trade(self, side, symbol, price, account_balance):
        """
        Check if a trade meets all safety and risk criteria.
        Returns True if approved, False otherwise.
        """
        self._check_reset_daily()

        if self.trading_halted:
            logger.warning(f"Trade REJECTED: Daily drawdown limit hit. Trading halted until midnight UTC.")
            return False

        if self.open_positions_count >= self.MAX_OPEN_POSITIONS:
            logger.warning(f"Trade REJECTED: Max open positions ({self.MAX_OPEN_POSITIONS}) reached.")
            return False

        # Calculate position size in USD
        max_size_usd = account_balance * (self.MAX_POSITION_SIZE_PCT / 100.0)
        
        # We don't perform the actual sizing here, but we check if the requested trade 
        # is within safety bounds in the main loop call.
        
        return True

    def record_fill(self, pnl, account_balance):
        """
        Update daily PnL tracker and check for drawdown halt.
        pnl: Profit/Loss of the closed position in USD.
        """
        self._check_reset_daily()
        self.daily_pnl += pnl
        
        # Calculate drawdown % relative to balance
        drawdown_pct = (abs(self.daily_pnl) / account_balance) * 100.0 if self.daily_pnl < 0 else 0
        
        if self.daily_pnl < 0 and drawdown_pct >= self.MAX_DAILY_DRAWDOWN_PCT:
            self.trading_halted = True
            logger.error("DAILY DRAWDOWN LIMIT HIT — trading halted")
        
        logger.info(f"PnL Recorded: ${pnl:.2f} | Daily Total: ${self.daily_pnl:.2f} | Status: {'HALTED' if self.trading_halted else 'OK'}")

    def get_status(self):
        return {
            "trading_halted": self.trading_halted,
            "daily_pnl": self.daily_pnl,
            "open_positions": self.open_positions_count
        }

# Singleton instance
risk_manager = RiskManager()
