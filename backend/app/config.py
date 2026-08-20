from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vector PDF Suite"
    max_upload_bytes: int = 100 * 1024 * 1024
    cache_ttl_seconds: int = 3600
    cache_max_bytes: int = 500 * 1024 * 1024
    task_timeout_seconds: int = 300
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    model_config = SettingsConfigDict(env_prefix="PDFSUITE_")


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)

