from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./aquavia_dev.db"
    secret_key: str = ""
    log_level: str = "INFO"
    max_batch_events: int = 500
    max_clock_skew_seconds: int = 300
    session_ttl_seconds: int = 8 * 3600
    login_max_failures: int = 5
    login_window_seconds: int = 900
    online_max_age_seconds: int = 900
    delayed_max_age_seconds: int = 7200

    @model_validator(mode="after")
    def _fail_early(self) -> "Settings":
        if self.app_env == "production" and (
            not self.secret_key or self.secret_key.startswith("REPLACE")
        ):
            raise ValueError("SECRET_KEY must be set to a real secret in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
