import os
from pathlib import Path
import hashlib

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GBNF_EXPERIMENT_")

    # data_directory holds run directories and nothing else. The prepared corpus is
    # rebuildable from a pinned commit and the docker context, so it is a cache,
    # not evidence, and it does not belong in the tree the runs are banked in.
    data_directory: Path = PACKAGE_ROOT / "data"
    prepared_directory: Path = CACHE_HOME / "ports" / "gbnf-experiment" / "prepared"
    root_directory: Path = PACKAGE_ROOT
    docker_directory: Path = PACKAGE_ROOT / "docker"
    # The merge of GBNF PR #81: nearest upstream ancestor of the v0 clone's local commits.
    gbnf_commit: str = "13f1aca495d11e160fffd68c4ba299a2415909d8"
    image_tag: str = "gbnf-prepare:latest"

    @property
    def prepare_docker_directory(self) -> Path:
        return self.docker_directory / "gbnf-prepare"


def compute_prepare_cache_key(gbnf_commit: str, docker_directory: Path) -> str:
    digests = [
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(docker_directory.rglob("*"))
        if path.is_file()
    ]
    return hashlib.sha256("".join([gbnf_commit, *digests]).encode()).hexdigest()[:16]


settings = Settings()
prepare_cache_key = compute_prepare_cache_key(
    settings.gbnf_commit, settings.prepare_docker_directory
)
