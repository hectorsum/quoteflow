import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    approval_threshold_usd: float = 10_000.0
    checkpoint_db_path: str = "quoteflow.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
