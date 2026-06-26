import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    approval_threshold_usd: float = 10_000.0

    # Rutas de SQLite. En producción apuntar a un volumen persistente
    # (ej. CHECKPOINT_DB_PATH=/data/quoteflow.db, DATABASE_PATH=/data/quoteflow_meta.db).
    checkpoint_db_path: str = "quoteflow.db"
    database_path: str = "./quoteflow.db"

    # Origen del frontend permitido por CORS (coma-separado para múltiples).
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins(self) -> list[str]:
        origins = {o.strip() for o in self.frontend_url.split(",") if o.strip()}
        origins.add("http://localhost:3000")  # siempre permitir desarrollo local
        return sorted(origins)


settings = Settings()
