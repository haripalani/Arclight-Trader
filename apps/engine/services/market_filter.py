import pandas as pd

class MarketFilter:
    """
    Detects unfavorable market conditions using ATR.
    Blocks trading during extreme volatility or dead sideways markets.
    Only math. Zero discretion.
    """

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        if df is None or len(df) < period + 1:
            return 0.0
        df = df.copy()
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['prev_close'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'prev_close']].apply(
            lambda row: max(
                row['high'] - row['low'],
                abs(row['high'] - row['prev_close']),
                abs(row['low'] - row['prev_close'])
            ), axis=1
        )
        return round(df['tr'].rolling(window=period).mean().iloc[-1], 4)

    @staticmethod
    def is_tradeable(df: pd.DataFrame) -> tuple[bool, str]:
        """
        Returns (is_tradeable, reason).
        """
        if df is None or len(df) < 30:
            return False, "Insufficient market data"

        atr = MarketFilter.calculate_atr(df)
        last_price = df['close'].iloc[-1]
        atr_pct = (atr / last_price) * 100

        # Dead market: ATR too low = sideways, no edge
        if atr_pct < 0.05:
            return False, f"Dead market: ATR={atr_pct:.3f}% (below 0.05% threshold)"

        # Extreme volatility: ATR too high = unpredictable, too risky
        if atr_pct > 3.0:
            return False, f"Extreme volatility: ATR={atr_pct:.3f}% (above 3.0% threshold)"

        # Volume check: last candle volume must exceed 50% MA
        df['volume'] = pd.to_numeric(df['volume'])
        vol_ma = df['volume'].rolling(20).mean().iloc[-1]
        last_vol = df['volume'].iloc[-1]
        if last_vol < vol_ma * 0.5:
            return False, f"Low volume: {last_vol:.0f} < 50% of MA {vol_ma:.0f}"

        return True, "Market conditions OK"

    @staticmethod
    def volume_score(df: pd.DataFrame) -> int:
        """Returns volume contribution score (0-30)."""
        if df is None or len(df) < 20:
            return 0
        df = df.copy()
        df['volume'] = pd.to_numeric(df['volume'])
        vol_ma = df['volume'].rolling(20).mean().iloc[-1]
        last_vol = df['volume'].iloc[-1]
        ratio = last_vol / vol_ma if vol_ma > 0 else 0

        if ratio >= 2.0:
            return 30   # strong volume spike
        elif ratio >= 1.5:
            return 20
        elif ratio >= 1.0:
            return 10
        return 0        # weak volume = no edge

market_filter = MarketFilter()
