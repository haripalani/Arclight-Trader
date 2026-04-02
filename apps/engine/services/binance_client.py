try:
    from binance import AsyncClient
except ImportError:
    from binance.client import AsyncClient
from core.config import settings
from core.logger import logger
import pandas as pd

class BinanceClient:
    def __init__(self):
        self.client = None
        self.is_testnet = (settings.binance_mode == "testnet")

    async def get_client(self):
        if self.client is None:
            # Allow initialization without keys for public endpoints (klines)
            # but log warning that trading will fail.
            key = settings.api_key if settings.api_key else None
            secret = settings.api_secret if settings.api_secret else None
            
            if not key:
                logger.warning("No BINANCE_API_KEY provided. Only public data (klines) will work.")
                
            self.client = await AsyncClient.create(
                key, 
                secret, 
                testnet=self.is_testnet
            )
        return self.client

    async def get_klines(self, symbol: str, interval: str, limit: int = 100):
        try:
            client = await self.get_client()
            klines = await client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['close'] = pd.to_numeric(df['close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            return None

    async def close(self):
        if self.client:
            await self.client.close_connection()

binance_client = BinanceClient()
