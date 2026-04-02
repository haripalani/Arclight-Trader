import pandas as pd

class RSIService:
    """
    Purely mathematical RSI calculation.
    No emotion. No discretion. Numbers only.
    """

    @staticmethod
    def calculate(df: pd.DataFrame, period: int = 14) -> float:
        if df is None or len(df) < period + 1:
            return 50.0  # neutral fallback

        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss.replace(0, 1e-10)  # avoid div by zero
        rsi = 100 - (100 / (1 + rs))

        return round(rsi.iloc[-1], 2)

    @staticmethod
    def score(rsi: float, signal: str) -> int:
        """
        Returns RSI contribution score (0-30).
        Penalizes overbought on BUY, oversold on SELL.
        """
        if signal == "BUY":
            if rsi < 30:
                return 30   # strong oversold — high probability
            elif rsi < 50:
                return 20
            elif rsi < 65:
                return 10
            else:
                return 0    # overbought on a BUY = blocked
        elif signal == "SELL":
            if rsi > 70:
                return 30   # strong overbought — high probability
            elif rsi > 50:
                return 20
            elif rsi > 35:
                return 10
            else:
                return 0    # oversold on a SELL = blocked
        return 0

rsi_service = RSIService()
