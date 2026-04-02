# Arclight Trading Engine (Python)

The execution layer for the Arclight ecosystem. This engine pulls live market ticks, processes them via a multi-layered trading algorithm, and executes orders directly on the Binance Exchange.

## Core Architecture
- **Market Filters**: Checks base volume and ATR to ensure sufficient market liquidity and motion.
- **Strategy Service**: Houses the institutional trading logic (`calculate_statistical_arbitrage`, `calculate_trend_following`, `calculate_ml_alpha`, etc.).
- **Strategy Selector Engine**: A dynamic regime-classification system that analyzes volatility and trend trajectory. It automatically swaps between Statistical Arbitrage during chop/volatility, and Systematic Momentum (Trend Following) during breakouts.
- **API Polling**: Fetches the `ml_alpha_bias` dynamically from the NestJS Evolution Brain on a scheduled tick.

## Execution Matrix
1. **Volatile Regime** -> `Stat Arb`
2. **Trending Regime** -> `Trend Following`
3. **Ranging Regime** -> `ML Alpha` + `Core EMA` Fallback

## Setup
Handled automatically by the `docker-compose` network.
```bash
# To test locally without Docker
pip install -r requirements.txt
python main.py
```
