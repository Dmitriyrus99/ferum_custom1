import os

from dotenv import load_dotenv

from typing import Optional

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ERP_API_URL: str = os.getenv("ERP_API_URL", "http://localhost:8000")
    ERP_API_KEY: Optional[str] = os.getenv("ERP_API_KEY")
    ERP_API_SECRET: Optional[str] = os.getenv("ERP_API_SECRET")
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
