from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parents[1]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GBNF_EXPERIMENT_")

    # data/runs is the seam between porting/ and analysis/: written here, read there.
    data_directory: Path = REPO_ROOT / "data" / "runs"
    root_directory: Path = PACKAGE_ROOT
    docker_directory: Path = PACKAGE_ROOT / "docker"
    # The merge of GBNF PR #81: nearest upstream ancestor of the v0 clone's local commits.
    gbnf_commit: str = "13f1aca495d11e160fffd68c4ba299a2415909d8"
    # A name, not a tag: the tag carries the condition the image was built for.
    image_name: str = "gbnf-prepare"

    @property
    def prepare_docker_directory(self) -> Path:
        return self.docker_directory / "gbnf-prepare"


settings = Settings()
