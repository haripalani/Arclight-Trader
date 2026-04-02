import logging
import sys
import httpx
import json
import datetime
from core.config import settings

# Phase 5: Structured JSON Logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "event_type": getattr(record, "event_type", "generic"),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields passed in 'extra'
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName", "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name", "pathname", "process", "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                log_entry[key] = value
                
        return json.dumps(log_entry)

# Standard local logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger("TradingEngine")

class RemoteLogger:
    """Sends logs to the NestJS Backend API"""
    
    @staticmethod
    async def log(event_type: str, message: str, metadata: dict = None):
        try:
            # Also log locally with structured data
            logger.info(message, extra={"event_type": event_type, "metadata": metadata or {}})
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.api_url}/log",
                    json={
                        "level": "info",
                        "event_type": event_type,
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
