import redis
import os
from core.config import settings
from core.logger import logger

class RedisClient:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                host = os.getenv("REDIS_HOST", "redis")
                port = int(os.getenv("REDIS_PORT", 6379))
                password = os.getenv("REDIS_PASSWORD")
                
                self._client = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    decode_responses=True,
                    socket_timeout=5
                )
                # Test connection
                self._client.ping()
                logger.info("Successfully connected to Redis.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._client = None
        return self._client

redis_client = RedisClient()
