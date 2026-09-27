from pathlib import Path

from python_on_whales import docker

from ..config import settings

REFERENCE_PATH = "/reference"


def prepare_image_tag(
    *,
    source_language: str,
    include_python_tests: bool,
    include_typescript_tests: bool,
) -> str:
    """One tag per condition, so the eight images coexist instead of overwriting."""
    return (
        f"{settings.image_name}:source-{source_language}"
        f"_python-tests-{'on' if include_python_tests else 'off'}"
        f"_typescript-tests-{'on' if include_typescript_tests else 'off'}"
    )


def prepare_reference_implementation(
    *,
    output_directory: Path,
    source_language: str,
    include_python_tests: bool,
    include_typescript_tests: bool,
    debug: bool,
) -> Path:
    """Build the prepare image for one condition and copy /reference out of it.

    The image decides what the agent sees: it filters the source tree and
    generates only the flagged suites. The host copies the folder out whole and
    selects nothing, so there is one place to read the corpus rule from.

    The image is never run. `docker create` is enough to give `docker cp` a
    filesystem to read, and a container that never starts cannot write.
    """
    tag = prepare_image_tag(
        source_language=source_language,
        include_python_tests=include_python_tests,
        include_typescript_tests=include_typescript_tests,
    )
    docker.build(
        settings.prepare_docker_directory,
        tags=tag,
        build_args={
            "GBNF_COMMIT": settings.gbnf_commit,
            "SOURCE_LANGUAGE": source_language,
            "INCLUDE_PYTHON_TESTS": str(include_python_tests).lower(),
            "INCLUDE_TYPESCRIPT_TESTS": str(include_typescript_tests).lower(),
        },
        progress="tty" if debug else False,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    container = docker.create(tag)
    try:
        docker.copy((container, REFERENCE_PATH), output_directory)
    finally:
        container.remove()
    return output_directory / Path(REFERENCE_PATH).name
