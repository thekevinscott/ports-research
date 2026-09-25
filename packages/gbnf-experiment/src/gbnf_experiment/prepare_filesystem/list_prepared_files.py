from python_on_whales import docker

from .build_prepare_image import build_prepare_image

LISTING = "/prepared.list"


def list_prepared_files(*, debug: bool) -> list[str]:
    """Every file the prepare stage left under /prepared, relative to it."""
    image = build_prepare_image(debug=debug)
    return docker.run(image, ["cat", LISTING], remove=True).splitlines()
