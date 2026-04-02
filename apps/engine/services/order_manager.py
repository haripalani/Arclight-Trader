from binance.enums import *
from services.binance_client import binance_client
from core.logger import logger, engine_logger
from core.config import settings
from services.redis_client import redis_client
import time
import asyncio

class OrderManager:
    async def place_market_order(self, symbol: str, side: str, quantity: float):
        """
        Places a market order on Binance with deduplication and rate limiting.
        side: SIDE_BUY or SIDE_SELL
        """
        # Phase 4: Order Deduplication
        timestamp_rounded = int(time.time() // 5) * 5
        dedup_key = f"order_dedup:{symbol}:{side}:{timestamp_rounded}"
        
        if redis_client.client:
            if redis_client.client.get(dedup_key):
                logger.warning(f"Duplicate order skipped: {symbol} {side}")
                return None
            redis_client.client.setex(dedup_key, 60, "1")

        # Phase 4: Rate Limit Tracking
        if redis_client.client:
            weight_key = "binance_rate_limit:weight"
            current_weight = redis_client.client.get(weight_key)
            if current_weight and int(current_weight) > 800:
                logger.warning(f"Rate limit reached (weight {current_weight}). Pausing 10s.")
                await asyncio.sleep(10)
            
            # Increment weight (market order weight is typically 1-10 depending on symbol/account)
            redis_client.client.incrby(weight_key, 10)
            if not redis_client.client.ttl(weight_key) > 0:
                redis_client.client.expire(weight_key, 60)

        try:
            client = await binance_client.get_client()
            logger.info(f"Placing {side} Market Order for {symbol} (Qty: {quantity})")
            
            order = await client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            msg = f"ORDER EXECUTED: {side} {symbol} @ {order.get('fills', [{}])[0].get('price', 'Market')}"
            logger.info(msg)
            await engine_logger.log("info", msg, order)
            return order
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            await engine_logger.log("error", f"Order failed: {e}")
            return None

    async def get_symbol_info(self, symbol: str):
        client = await binance_client.get_client()
        return await client.get_symbol_info(symbol)

order_manager = OrderManager()
