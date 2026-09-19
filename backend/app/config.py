from __future__ import annotations

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "BuktiSaham"
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    free_only_market_data: bool = True
    market_data_provider: str = "yfinance"
    yfinance_request_timeout_seconds: int = 20
    yfinance_cache_ttl_seconds: int = 300

    ai_review_enabled: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    ollama_timeout_seconds: int = 120

    database_url: str = "sqlite:///./buktisaham-local.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"

    policy_buy_expected_return: float = 0.15
    policy_sell_expected_return: float = -0.10
    policy_max_bear_downside: float = -0.25
    policy_min_confidence: float = 45.0
    policy_min_liquidity: float = 50.0
    policy_min_technical: float = 55.0

    @field_validator("market_data_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        return value.strip().lower()

    def enforce_market_data_policy(self) -> None:
        if self.free_only_market_data and self.market_data_provider != "yfinance":
            raise RuntimeError(
                "FREE_ONLY_MARKET_DATA=true permits only MARKET_DATA_PROVIDER=yfinance in this MVP. "
                "No paid-provider fallback is enabled."
            )

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.enforce_market_data_policy()
    return settings
