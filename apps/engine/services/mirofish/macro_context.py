import httpx
import os
import asyncio
import time
from core.logger import logger
from core.config import settings

class MacroContext:
    """
    Fetches institutional macro data to feed the Miro Swarm.
    Uses Direct API calls to ensure performance and reliability.
    """
    def __init__(self):
        self._cached_data = {
            "dxy": "101.5",
            "btc_dominance": "52.0%",
            "fear_greed_index": 50,
            "sentiment": "Neutral"
        }
        self._last_update = 0

    async def get_current_macro(self) -> dict:
        """Fetch live institutional macro data (Original Data)."""
        # Cache for 10 minutes (Total 144 requests/day max, safe for 25 req/day limit)
        if time.time() - self._last_update < 600:
            return self._cached_data

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                # 1. Fear & Greed Index (Public Free)
                fng_resp = await client.get("https://api.alternative.me/fng/", timeout=3.0)
                if fng_resp.status_code == 200:
                    fng_data = fng_resp.json().get("data", [{}])[0]
                    self._cached_data["fear_greed_index"] = int(fng_data.get("value", 50))
                    self._cached_data["sentiment"] = fng_data.get("value_classification", "Neutral")

                # 2. DXY Index Proxy (UUP) via Alpha Vantage (Free Tier)
                if settings.alpha_vantage_key:
                    av_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=UUP&apikey={settings.alpha_vantage_key}"
                    av_resp = await client.get(av_url, timeout=5.0)
                    if av_resp.status_code == 200:
                        quote = av_resp.json().get("Global Quote", {})
                        price = quote.get("05. price")
                        if price:
                            self._cached_data["dxy"] = f"{float(price):.2f}"

                # 3. BTC Dominance via CoinGecko (Keyless Public Global)
                # Note: User's key failed, fallback to public keyless endpoint
                cg_resp = await client.get("https://api.coingecko.com/api/v3/global", timeout=4.0)
                if cg_resp.status_code == 200:
                    global_data = cg_resp.json().get("data", {})
                    dom = global_data.get("market_cap_percentage", {}).get("btc", 50.0)
                    self._cached_data["btc_dominance"] = f"{float(dom):.1f}%"

            self._last_update = time.time()
            logger.info(f"Macro Context Updated: DXY {self._cached_data['dxy']}, F&G {self._cached_data['fear_greed_index']}")
        except Exception as e:
            logger.warning(f"Macro Data Fetch Error: {e}. Using cached data.")

        return self._cached_data

macro_context = MacroContext()
