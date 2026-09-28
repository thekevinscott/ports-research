from pathlib import Path

from python_on_whales import docker

from ..config import settings
from .assemble_whitelist.assemble_whitelist import assemble_whitelist

SHARED_PATH = "/shared"


def prepare_image_tag(
    *,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
) -> str:
    """One tag per condition, so the sixteen images coexist instead of overwriting."""
    return (
        f"{settings.image_name}:{source_language}"
        f"_unit-{'on' if include_unit_tests else 'off'}"
        f"_source-integration-{'on' if include_source_integration_tests else 'off'}"
        f"_target-integration-{'on' if include_target_integration_tests else 'off'}"
    )


def prepare_reference_implementation(
    *,
    output_directory: Path,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
) -> Path:
    """Build the prepare image for one condition and copy /shared out of it.

    The condition reaches the image as one composed rsync filter, so the image
    never sees a flag or a language. The host copies the folder out whole and
    selects nothing, so there is one place to read the corpus rule from.

    The image is never run. `docker create` is enough to give `docker cp` a
    filesystem to read, and a container that never starts cannot write.
    """
    tag = prepare_image_tag(
        source_language=source_language,
        include_unit_tests=include_unit_tests,
        include_source_integration_tests=include_source_integration_tests,
        include_target_integration_tests=include_target_integration_tests,
    )
    docker.build(
        settings.prepare_docker_directory,
        tags=tag,
        build_args={
            "GBNF_COMMIT": settings.gbnf_commit,
            "RULES": assemble_whitelist(
                source_language,
                include_unit_tests=include_unit_tests,
                include_source_integration_tests=include_source_integration_tests,
                include_target_integration_tests=include_target_integration_tests,
            ),
        },
        progress="tty" if debug else False,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    container = docker.create(tag)
    try:
        docker.copy((container, SHARED_PATH), output_directory)
    finally:
        container.remove()
    return output_directory / Path(SHARED_PATH).name
