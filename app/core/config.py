from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFleet 2.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:////data/antigravity/smartfleet_backend/smartfleet.db"
    DB_ECHO: bool = False
    JWT_SECRET: str = "smartfleet-dev-secret-key-change-in-prod-nh66-kerala-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    BASE_DIR: str = "/data/antigravity/smartfleet_backend"
    UPLOAD_DIR: str = "/data/antigravity/smartfleet_backend/app/uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if not url or "spott.db" in url:
            return "sqlite+aiosqlite:////data/antigravity/smartfleet_backend/smartfleet.db"
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://")
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        return url

settings = Settings()
