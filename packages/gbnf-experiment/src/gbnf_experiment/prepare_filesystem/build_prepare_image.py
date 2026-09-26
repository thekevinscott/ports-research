from python_on_whales import docker

from ..config import settings


def build_prepare_image(*, debug: bool) -> str:
    """Build the prepare image: clone at pin, patch, install, test-writer."""
    docker.build(
        settings.prepare_docker_directory,
        tags=settings.image_tag,
        build_args={"GBNF_COMMIT": settings.gbnf_commit},
        progress="tty" if debug else False,
    )
    return settings.image_tag
