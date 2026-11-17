from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/shopsense"
    SECRET_KEY: str = "supersecretjwtkey_shopsense_internship_2026_demo_key_min32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days (prevents premature session expiration during internship demo & evaluation)
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    API_BASE_URL: str = "http://127.0.0.1:8000"
    COGS_RATIO: float = 0.70  # Assumed Cost of Goods Sold ratio (70%)
    ADMIN_REGISTRATION_SECRET: str = ""  # Strictly loaded from environment / .env, no hardcoded default

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
