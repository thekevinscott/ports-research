from pathlib import Path

from python_on_whales import docker

from .build_prepare_image import build_prepare_image

PREPARED_TESTS = "/prepared/tests"


def export_prepared_tests(*, into: Path, debug: bool) -> Path:
    """Copy the generated suites out of the prepare stage, for grading on the host.

    A stopped container and `docker cp`, so the files land owned by the caller.
    """
    image = build_prepare_image(debug=debug)
    container = docker.container.create(image)
    try:
        docker.container.copy((container, PREPARED_TESTS), into)
    finally:
        container.remove()
    return into / "tests"
