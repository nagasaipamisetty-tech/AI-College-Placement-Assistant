
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI College Placement Assistant"
    secret_key: str = "development-only-change-me"
    access_token_expire_minutes: int = 90
    database_url: str = "sqlite:///./placement_assistant.db"
    turso_database_url: str = ""
    turso_auth_token: str = ""
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()