from services.rsi_service import rsi_service
from services.market_filter import market_filter
from services.strategy_service import strategy_service
from services.strategy_selector import strategy_selector
from services.mirofish.adapter import mirofish_adapter
from services.macro_service import macro_service
import pandas as pd
import asyncio

SCORE_THRESHOLD = 60  # Minimum score to open the gate

class SignalScorer:
    """
    Aggregates all indicators into a composite score (0–120 max, threshold 60).
    
    Breakdown:
      Strategy Engine: 40 pts  (AI selected core trend/reversion direction)
      RSI Filter:      30 pts  (momentum confirmation)
      Volume Spike:    30 pts  (conviction filter)
      MiroFish Bonus:  +20 pts (swarm intelligence overlay)
    
    Gate opens only if score >= 60.
    """

    @staticmethod
    async def evaluate(df: pd.DataFrame, evolution_bias: str = "HOLD") -> dict:
        result = {
            "signal": "HOLD",
            "score": 0,
            "gate_open": False,
            "reason": "",
            "breakdown": {},
            "mirofish": None,
        }

        if df is None or len(df) < 30:
            result["reason"] = "Not enough data"
            return result

        # 1. Market condition gate (binary — fail fast)
        tradeable, market_reason = market_filter.is_tradeable(df)
        if not tradeable:
            result["reason"] = f"Market Gate BLOCKED: {market_reason}"
            return result

        # 2. AI Strategy Selection Engine (0-40 pts)
        signal, active_strategy = strategy_selector.select_strategy_signal(df, strategy_service, evolution_bias)
        if signal == "HOLD":
            result["reason"] = f"No active signal from {active_strategy}"
            return result
        strategy_score = 40

        # 3. RSI score (0-30 pts)
        rsi_val = rsi_service.calculate(df)
        rsi_sc  = rsi_service.score(rsi_val, signal)

        # 4. Volume score (0-30 pts)
        vol_sc = market_filter.volume_score(df)

        # 5. MiroFish swarm bonus (0-20 pts)
        last_price = float(df['close'].iloc[-1])
        mf_signal = await mirofish_adapter.get_market_signal(
            symbol="BTC/USDT",
            price=last_price,
            ema_signal=signal,
            rsi=rsi_val,
        )

        # Bonus only if MiroFish agrees with Strategy direction
        mirofish_bonus = 0
        if signal == "BUY" and mf_signal.direction == "BULLISH":
            mirofish_bonus = mf_signal.bonus_score
        elif signal == "SELL" and mf_signal.direction == "BEARISH":
            mirofish_bonus = mf_signal.bonus_score

        macro_bonus = 0
        try:
            dxy_val = float(macro_service.last_data.get("dxy", "101.5"))
            # If DXY > 102 (strong dollar), it's bearish for BTC
            if signal == "BUY" and dxy_val > 102.0:
                macro_bonus = -10
            elif signal == "SELL" and dxy_val > 102.0:
                macro_bonus = 10
        except:
            pass

        total_score = strategy_score + rsi_sc + vol_sc + mirofish_bonus + macro_bonus
        # Clamp score between 0 and 120
        total_score = max(0, min(120, total_score))

        result.update({
            "signal": signal,
            "score": total_score,
            "gate_open": total_score >= SCORE_THRESHOLD,
            "reason": (
                f"Gate OPEN [{active_strategy}] — ALL conditions met"
                if total_score >= SCORE_THRESHOLD
                else f"Gate BLOCKED [{active_strategy}] — Score {total_score} < threshold {SCORE_THRESHOLD}"
            ),
            "breakdown": {
                "strategy_score": strategy_score,
                "active_strategy": active_strategy,
                "rsi":            rsi_sc,
                "rsi_value":      rsi_val,
                "volume":         vol_sc,
                "mirofish_bonus": mirofish_bonus,
                "mirofish_dir":   mf_signal.direction,
                "mirofish_conf":  mf_signal.confidence,
                "macro_adjustment": macro_bonus,
            },
            "mirofish": {
                "direction":  mf_signal.direction,
                "confidence": mf_signal.confidence,
                "excerpt":    mf_signal.excerpt,
                "bonus":      mirofish_bonus,
            }
        })
        return result

signal_scorer = SignalScorer()
