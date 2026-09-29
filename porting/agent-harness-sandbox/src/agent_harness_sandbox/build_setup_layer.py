import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from python_on_whales import docker

from .config import SETUP_LAYER_SUFFIX
from .errors import AgentHarnessSandboxError


def build_setup_layer(*, base_image: str, setup_script: str | Path, debug: bool) -> str:
    """Build a layer on BASE_IMAGE that runs the caller's setup script, and return its tag.

    The build stage has network open, by design: it is the only place a package
    registry is reachable, so a caller's dependency install belongs here and the
    running agent needs no registry egress of its own. The script runs as root,
    the same as an agent's own layer installs its CLI, then setuid bits picked up
    along the way are dropped before handing back to `node`.
    """
    script = Path(setup_script)
    if not script.exists():
        raise AgentHarnessSandboxError(f"{script} does not exist")

    name, _, tag = base_image.partition(":")
    setup_image = f"{name}{SETUP_LAYER_SUFFIX}:{tag or 'latest'}"

    progress = "tty" if debug else False
    with TemporaryDirectory() as context:
        context_dir = Path(context)
        shutil.copy(script, context_dir / script.name)
        dockerfile = context_dir / "Dockerfile"
        dockerfile.write_text(
            f"FROM {base_image}\n"
            "\n"
            "USER root\n"
            "\n"
            f"COPY {script.name} /tmp/{script.name}\n"
            f"RUN chmod +x /tmp/{script.name} && /tmp/{script.name}\n"
            "\n"
            "RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} +\n"
            "\n"
            "USER node\n"
        )
        docker.build(context_dir, tags=setup_image, file=dockerfile, progress=progress)
    return setup_image
