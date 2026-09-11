import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    datasets_dir: Path = Path(os.getenv("DATASETS_DIR", "datasets"))
    reports_dir: Path = Path(os.getenv("REPORTS_DIR", "reports"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()