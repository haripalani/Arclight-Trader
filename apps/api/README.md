# Arclight Trading API (NestJS)

The API serves as the centralized orchestration and UI backend for the Arclight Trading Platform. It bridges the Python Trading Engine, the PostgreSQL Database, and the Web Dashboard.

## Core Features
- **Evolution Brain (`evolution.service.ts`)**: The AI reasoning layer. It continuously analyzes past trade logs (wins/losses/PnL) and queries an LLM (Qwen/NVIDIA) to adjust system parameters. It actively outputs the `ml_alpha_bias`, acting as an explicit override or suggestion to the Python execution engine.
- **REST Endpoints**: Provides real-time websocket and REST links for the dashboard to track running PnL, active trades, and bot states.
- **Data Persistence (Prisma)**: Manages historical trades, SkillProfiles, and engine metrics.

## Setup
```bash
npm install
npm run start:dev
```
