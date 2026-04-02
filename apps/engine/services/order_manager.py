from binance.enums import *
from services.binance_client import binance_client
from core.logger import logger, engine_logger
from core.config import settings

class OrderManager:
    async def place_market_order(self, symbol: str, side: str, quantity: float):
        """
        Places a market order on Binance.
        side: SIDE_BUY or SIDE_SELL
        """
        try:
            client = await binance_client.get_client()
            logger.info(f"Placing {side} Market Order for {symbol} (Qty: {quantity})")
            
            # Using Sync client wrapper until fully transitioned or using call_coroutine
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
