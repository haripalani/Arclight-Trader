# Risk Management Service

This service acts as the capital protection layer for the Arclight Trading Engine. It ensures that the execution engine strictly follows hard-coded risk constraints, automatically closing positions or restricting sizing even if the Strategy or ML Alpha models issue contrasting signals.

## Core Features
- **Dynamic Position Sizing**: Calculates trade size dynamically based on the current available balance and the predefined `RISK_PER_TRADE` (default 1%).
- **Hard Stop Losses**: Monitors live pricing and instantly requests an exit if the position crosses the `STOP_LOSS_PCT` threshold (default 2%), preventing catastrophic account drawdowns.
- **Take Profit Targets**: Automatically initiates a close order if the position hits the `TAKE_PROFIT_PCT` threshold (default 4%).
- **Maximum Drawdown Limits**: Prevents the bot from initiating new sequences if the global `MAX_DRAWDOWN` limit is hit on the account.

## Architecture
The `risk_manager.py` is invoked inside `main.py` directly alongside the Strategy engine.
1. During the polling loop, `risk_manager.should_exit()` evaluates open positions.
2. If `should_exit` returns a trigger, the Trade Gate is preempted and a Market close order is fired asynchronously.
3. Upon Trade Entry, `calculate_position_size()` ensures capital limits are enforced.
