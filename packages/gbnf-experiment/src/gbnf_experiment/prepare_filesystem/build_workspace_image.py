import hashlib
from pathlib import Path

from python_on_whales import docker

from ..config import settings


def build_workspace_image(*, agent_image: str, files: list[Path], debug: bool) -> str:
    """Bake exactly files, out of the prepared tree, onto agent_image.

    Tagged by the list, so two conditions never race over one tag. The pin and
    the agent image still bust the cache; the manifest names the result by id.
    """
    listing = "\n".join(path.as_posix() for path in files)
    digest = hashlib.sha256(listing.encode()).hexdigest()[:16]
    tag = f"{settings.workspace_image_repository}:{digest}"
    docker.build(
        settings.workspace_docker_directory,
        tags=tag,
        build_args={
            "GBNF_COMMIT": settings.gbnf_commit,
            "AGENT_IMAGE": agent_image,
            "FILES": listing,
        },
        progress="tty" if debug else False,
    )
    return tag
