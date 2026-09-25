from python_on_whales import docker

from ..config import settings


def build_prepare_image(*, debug: bool) -> str:
    """Build the prepare stage alone: clone at pin, patch, install, test-writer."""
    docker.build(
        settings.workspace_docker_directory,
        target="prepare",
        tags=settings.prepare_image_tag,
        build_args={"GBNF_COMMIT": settings.gbnf_commit},
        progress="tty" if debug else False,
    )
    return settings.prepare_image_tag
