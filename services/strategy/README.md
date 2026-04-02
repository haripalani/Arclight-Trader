# Strategy Service & Selection Engine

This service manages the core trading models and the AI Strategy Selector that drives the Arclight Trading Engine. It automatically identifies the current market regime and shifts into the most statistically optimal model.

## Available Trading Strategies
- **Statistical Arbitrage (Mean Reversion)**: Uses Bollinger Bands and standard deviations. It identifies over-extended assets (overbought/oversold) and trades the reversion to the Mean. *Triggered during VOLATILE market regimes.*
- **Trend Following (Systematic Momentum)**: Uses MACD and Exponential Moving Averages (EMA). It identifies strong momentum shifts and rides the macro trend. *Triggered during TRENDING market regimes.*
- **ML/AI Alpha Engine**: Uses real-time insights from the LLM Evolution Brain to assert directional bias. *Triggered during NORMAL/RANGING market regimes or as a supplemental scoring factor.*
- **Core EMA Crossover**: The fallback momentum algorithm used heavily in earlier Arclight iterations.

## Architecture: The AI Strategy Selector
The `strategy_selector.py` engine sits in front of the strategy layer. Before executing a trade scan, it:
1. Calculates asset **Volatility** (standard deviation of recent percentage changes).
2. Calculates **Trend Strength** (relationship between short and long moving averages).
3. Selects the optimal execution strategy based on the mathematically proven regime.

This entirely removes human emotion and manual strategy-switching from the loop.
