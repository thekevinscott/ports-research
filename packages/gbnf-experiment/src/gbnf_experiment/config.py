from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GBNF_EXPERIMENT_")

    # data_directory holds run directories and nothing else. The workspace the
    # agent sees is an image, rebuilt from the pin and the docker context and
    # named in the manifest by id.
    data_directory: Path = PACKAGE_ROOT / "data"
    root_directory: Path = PACKAGE_ROOT
    docker_directory: Path = PACKAGE_ROOT / "docker"
    # The merge of GBNF PR #81: nearest upstream ancestor of the v0 clone's local commits.
    gbnf_commit: str = "13f1aca495d11e160fffd68c4ba299a2415909d8"
    prepare_image_tag: str = "gbnf-prepare:latest"
    workspace_image_repository: str = "gbnf-workspace"

    @property
    def workspace_docker_directory(self) -> Path:
        return self.docker_directory / "gbnf-workspace"


settings = Settings()
