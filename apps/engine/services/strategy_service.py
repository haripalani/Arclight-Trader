import pandas as pd
import numpy as np
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class StrategyService:
    @staticmethod
    def calculate_ema_crossover(df: pd.DataFrame):
        if df is None or len(df) < settings.slow_ema:
            return "WAITING"

        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(span=settings.fast_ema, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=settings.slow_ema, adjust=False).mean()

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Crossover Detection
        if prev_row['ema_fast'] <= prev_row['ema_slow'] and last_row['ema_fast'] > last_row['ema_slow']:
            return "BUY"
        elif prev_row['ema_fast'] >= prev_row['ema_slow'] and last_row['ema_fast'] < last_row['ema_slow']:
            return "SELL"
        
        return "HOLD"
        
    @staticmethod
    def calculate_statistical_arbitrage(df: pd.DataFrame, window=20, num_std=2):
        """Mean Reversion using Bollinger Bands"""
        if df is None or len(df) < window:
            return "WAITING"
            
        df_calc = df.copy()
        df_calc['sma'] = df_calc['close'].rolling(window=window).mean()
        df_calc['std'] = df_calc['close'].rolling(window=window).std()
        df_calc['upper_band'] = df_calc['sma'] + (df_calc['std'] * num_std)
        df_calc['lower_band'] = df_calc['sma'] - (df_calc['std'] * num_std)
        
        last_row = df_calc.iloc[-1]
        
        # Mean Reversion Logic
        if last_row['close'] < last_row['lower_band']:
            return "BUY"  # Price is below lower band (oversold)
        elif last_row['close'] > last_row['upper_band']:
            return "SELL" # Price is above upper band (overbought)
            
        return "HOLD"
        
    @staticmethod
    def calculate_trend_following(df: pd.DataFrame, fast_period=12, slow_period=26, signal_period=9):
        """Trend Following using MACD"""
        if df is None or len(df) < slow_period + signal_period:
            return "WAITING"
            
        df_calc = df.copy()
        df_calc['ema_fast'] = df_calc['close'].ewm(span=fast_period, adjust=False).mean()
        df_calc['ema_slow'] = df_calc['close'].ewm(span=slow_period, adjust=False).mean()
        df_calc['macd'] = df_calc['ema_fast'] - df_calc['ema_slow']
        df_calc['signal_line'] = df_calc['macd'].ewm(span=signal_period, adjust=False).mean()
        
        last_row = df_calc.iloc[-1]
        prev_row = df_calc.iloc[-2]
        
        if prev_row['macd'] <= prev_row['signal_line'] and last_row['macd'] > last_row['signal_line']:
            return "BUY"
        elif prev_row['macd'] >= prev_row['signal_line'] and last_row['macd'] < last_row['signal_line']:
            return "SELL"
            
        return "HOLD"

    @staticmethod
    def calculate_ml_alpha(df: pd.DataFrame, ai_bias: str = "HOLD"):
        """
        Placeholder for ML-driven alpha (LLM generated signal).
        Will be fed by the evolutionary brain in Phase 3.
        """
        if ai_bias in ["BUY", "SELL"]:
            return ai_bias
        return "HOLD"

strategy_service = StrategyService()
