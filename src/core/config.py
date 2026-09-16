import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE_PATH = PROJECT_ROOT / ".env"


def log_settings():
    logger.info("Current Settings:")
    for key, value in settings.model_dump().items():
        # Mask secrets
        if "SECRET" in key or "KEY" in key or "PASSWORD" in key:
            value = value[:5] + "...(MASKED)..." + value[-5:]
        logger.info(f"  {key}: {value}")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Zack-Zack-Deutsch"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # Database
    DATABASE_URL: str = "sqlite:///./zz-deutsch.db"

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8080/api/v1/auth/google/callback"

    FRONTEND_URL: str = "http://localhost:5173"
    FRONTEND_CALLBACK_PATH: str = "/login/callback"

    # External Services
    DEEPL_API_KEY: str = ""

    class Config:
        env_file = ENV_FILE_PATH
        env_file_encoding = "utf-8"


settings = Settings()
