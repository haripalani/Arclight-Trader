import pandas as pd
import numpy as np

class StrategySelector:
    """
    Market Regime classification engine to automatically switch strategies.
    
    Regimes:
    - TRENDING: ADX proxy is high, use Trend Following.
    - VOLATILE: High ATR relative to price, use Statistical Arbitrage (Mean Reversion).
    - RANGING/DEFAULT: Normal behavior, use ML Alpha or fallback.
    """
    
    @staticmethod
    def get_market_regime(df: pd.DataFrame, window=14) -> str:
        if df is None or len(df) < window:
            return "DEFAULT"
            
        # 1. Calculate a simple Volatility metric (Std Dev of returns)
        returns = df['close'].pct_change().dropna()
        volatility = returns.rolling(window=window).std().iloc[-1] * np.sqrt(window)
        
        # 2. Approximate Trend Strength (Absolute difference between short and long SMA divided by close)
        sma_short = df['close'].rolling(window=7).mean().iloc[-1]
        sma_long = df['close'].rolling(window=21).mean().iloc[-1]
        trend_strength = abs(sma_short - sma_long) / df['close'].iloc[-1]
        
        # Absolute thresholds based on typical crypto metrics (can be evolved later)
        # Higher volatility threshold = choppy, mean reversion.
        if volatility > 0.05: # High Volatility 
            return "VOLATILE"
            
        # Higher trend strength = directional.
        if trend_strength > 0.02:
            return "TRENDING"
            
        return "DEFAULT"

    def select_strategy_signal(self, df: pd.DataFrame, strategy_service, evolution_bias: str = "HOLD") -> tuple[str, str]:
        """
        Determines the current market regime and runs the optimally suited strategy.
        Returns: (signal, strategy_name)
        """
        regime = self.get_market_regime(df)
        
        if regime == "VOLATILE":
            signal = strategy_service.calculate_statistical_arbitrage(df)
            return signal, "Statistical Arbitrage"
            
        elif regime == "TRENDING":
            signal = strategy_service.calculate_trend_following(df)
            return signal, "Trend Following"
            
        else:
            # Ranging, use ML alpha or fallback to basic EMA
            signal = strategy_service.calculate_ml_alpha(df, evolution_bias)
            if signal == "HOLD":
                # Fallback to standard logic if ML Alpha is undecided
                signal = strategy_service.calculate_ema_crossover(df)
            return signal, "ML Alpha / Core EMA"

strategy_selector = StrategySelector()
