"""Integration tests: Docker mocked at the python_on_whales boundary, the way botbox's own are."""

from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

PROXY_IMAGE = "botbox-proxy:latest"


class Daemon:
    """The Docker daemon as botbox sees it: what it was asked to build and run, and what the run prints."""

    def __init__(self) -> None:
        self.builds: list[dict[str, Any]] = []
        self.runs: list[dict[str, Any]] = []
        self.removed: list[str] = []
        self.stdout = b""
        self.exit_code = 0

    @property
    def agent(self) -> dict[str, Any]:
        """The agent container: every run that is not the proxy sidecar."""
        [run] = [r for r in self.runs if r["image"] != PROXY_IMAGE]
        return run


@pytest.fixture
def daemon() -> Daemon:
    return Daemon()


@pytest.fixture(autouse=True)
def docker(daemon: Daemon) -> Iterator[None]:
    """Every daemon-facing call botbox makes, patched where python_on_whales defines it."""
    with (
        patch("python_on_whales.docker.build", autospec=True) as build,
        patch("python_on_whales.docker.run", autospec=True) as run,
        patch("python_on_whales.docker.logs", autospec=True) as logs,
        patch("python_on_whales.docker.wait", autospec=True) as wait,
        patch("python_on_whales.docker.network", autospec=True) as network,
        patch("python_on_whales.docker.container", autospec=True) as container,
        patch("python_on_whales.utils.run", autospec=True),
    ):
        network.docker_cmd = ["docker"]

        def record_build(context: Path, **options: Any) -> None:
            daemon.builds.append({"context": Path(context), **options})

        def record_run(image: str, command: Sequence[str] = (), **options: Any) -> MagicMock:
            handle = MagicMock(name=image)
            daemon.runs.append({"image": image, "command": list(command), "handle": handle, **options})
            return handle

        def record_remove(containers: str | Sequence[str], **_options: Any) -> None:
            daemon.removed.extend([containers] if isinstance(containers, str) else containers)

        build.side_effect = record_build
        run.side_effect = record_run
        logs.side_effect = lambda *_args, **_options: iter([("stdout", daemon.stdout)])
        wait.side_effect = lambda *_args: daemon.exit_code
        container.remove.side_effect = record_remove
        yield
