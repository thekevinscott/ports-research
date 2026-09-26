import os
import shutil
from pathlib import Path

from python_on_whales import docker

from ..config import settings


def prepare_reference_implementation(*, output_directory: Path, debug: bool) -> Path:
    docker.build(
        settings.prepare_docker_directory,
        tags=settings.image_tag,
        build_args={"GBNF_COMMIT": settings.gbnf_commit},
        progress="tty" if debug else False,
    )
    staging_directory = output_directory.with_name(output_directory.name + ".staging")
    shutil.rmtree(staging_directory, ignore_errors=True)
    staging_directory.mkdir(parents=True)
    docker.run(
        settings.image_tag,
        user=f"{os.getuid()}:{os.getgid()}",
        volumes=[(str(staging_directory), "/prepared-output", "rw")],
        remove=True,
    )
    staging_directory.rename(output_directory)
    return output_directory
