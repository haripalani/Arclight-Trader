import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_key: str = os.getenv("BINANCE_API_KEY", "")
    api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    testnet: bool = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
    
    api_url: str = os.getenv("API_URL", "http://localhost:9001")
    
    system_api_key: str = os.getenv("SYSTEM_API_KEY", "")
    user_id: str = os.getenv("USER_ID", "") 
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    
    # Phase 9: Real Trading
    binance_mode: str = os.getenv("BINANCE_MODE", "testnet") # "live" or "testnet"
    real_capital_limit: float = float(os.getenv("REAL_CAPITAL_LIMIT", "50.0")) # Max $50 for safe mode
    
    symbol: str = "BTCUSDT"
    interval: str = "1m"
    
    fast_ema: int = 9
    slow_ema: int = 21

    # Mirofish Adapter
    mirofish_url: str = os.getenv("MIROFISH_URL", "http://mirofish:5000")

    # Telegram
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- ZERO-COST PRODUCTION KEYS ---
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
