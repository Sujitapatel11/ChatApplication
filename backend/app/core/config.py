from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str = ""                  # optional — empty = disabled
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    @property
    def redis_enabled(self) -> bool:
        return bool(self.redis_url)


settings = Settings()
