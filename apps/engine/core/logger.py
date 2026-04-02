import logging
import sys
import httpx
import json
from core.config import settings

# Standard local logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("TradingEngine")

class RemoteLogger:
    """Sends logs to the NestJS Backend API"""
    
    @staticmethod
    async def log(level: str, message: str, metadata: dict = None):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.api_url}/log",
                    json={
                        "level": level,
                        "message": message,
                        "metadata": metadata or {}
                    },
                    headers={
                        "x-api-key": settings.system_api_key,
                        "x-user-id": settings.user_id
                    },
                    timeout=2.0
                )
        except Exception:
            # Fallback to local if remote fails
            logger.warning(f"Failed to send remote log: {message}")

engine_logger = RemoteLogger()
