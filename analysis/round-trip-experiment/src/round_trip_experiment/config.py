import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROUND_TRIP_EXPERIMENT_")

    # Back-translations bank here and never in a data/, so they cannot be mistaken for
    # forward ports or muddy the banked corpus.
    reverse_directory: Path = PACKAGE_ROOT / "reverse"
    staging_directory: Path = CACHE_HOME / "ports" / "round-trip-experiment" / "derivations"


settings = Settings()
