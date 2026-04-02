# Arclight Evolutionary Trading Platform 

Arclight is a multi-agent, automated AI trading system designed to evolve parameter logic over time seamlessly and execute trades with institutional-grade quant strategies.

## Project Structure
This is a monorepo containing multiple interconnected services:

- `/apps/engine` (Python): High-frequency polling and trade execution. Includes the dynamic Strategy Selection Engine that swaps between Trend Following, Statistical Arbitrage, and ML Alpha based on current market regimes.
- `/apps/api` (NestJS/TypeScript): The backend orchestrator, Prisma DB layer, and the **Evolution Brain**. Calls the LLM (NVIDIA APIs / Qwen) to generate the `ml_alpha_bias`.
- `/apps/web` (Next.js/React): The frontend dashboard to view real-time logs, chart performance, and observe the AI shifting the model's strategies.
- `/services/strategy`: Documentation and logic boundaries for the active quantitative models.

## AI Strategy Architecture
The Arclight system does not rely on simple static algorithms. It identifies:
1. **Volatile Markets**: Deploys Mean Reversion (Statistical Arbitrage via Bollinger deviation).
2. **Trending Markets**: Deploys Systematic Momentum (Continuous Trend Following via MACD validation).
3. **Ranging Markets**: Defer to the LLM's predictive bias fetched from the Evolution API loop.

## Deployment
```bash
docker-compose up -d --build
```
