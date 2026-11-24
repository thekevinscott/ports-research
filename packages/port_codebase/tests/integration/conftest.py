"""Integration tests: Botbox faked where port_codebase imports it."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from adocker import DockerException
from botbox import RunResult


class FakeBotbox:
    """What port_codebase asked the box for, and what the run prints."""

    boxes: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    kept: set[str]
    stdout = ""
    exit_code = 0

    def __init__(
        self, agent: Any, *, dockerfile: Path | None = None, allow: tuple[str, ...] = (), memory: str | None = None
    ) -> None:
        self.boxes.append({"agent": agent, "dockerfile": dockerfile, "allow": allow, "memory": memory})

    async def __aenter__(self) -> "FakeBotbox":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        return None

    async def run(
        self, command: str, *, mounts: Any = (), workdir: str | None = None, output: Path, keep: str
    ) -> RunResult:
        self.runs.append({"command": command, "mounts": mounts, "workdir": workdir, "output": output, "keep": keep})
        self.kept.add(keep)
        output.mkdir(parents=True, exist_ok=True)
        (output / "stdout.txt").write_text(self.stdout)
        return RunResult(exit_code=self.exit_code, container_name=keep)

    async def restart(
        self, name: str, command: str, *, mounts: Any = (), workdir: str | None = None, output: Path
    ) -> RunResult:
        self.runs.append({"restart": name, "command": command, "mounts": mounts, "workdir": workdir, "output": output})
        output.mkdir(parents=True, exist_ok=True)
        (output / "stdout.txt").write_text(self.stdout)
        return RunResult(exit_code=self.exit_code, container_name=name)


@pytest.fixture
def kept() -> set[str]:
    """The names of the containers the daemon holds."""
    return set()


@pytest.fixture(autouse=True)
def removed(kept: set[str]) -> Iterator[list[str]]:
    """The kept containers and volumes removed, as `container:<name>` and `volume:<name>`."""
    removals: list[str] = []

    class FakeContainer:
        def __init__(self, name: str) -> None:
            self.name = name

        async def inspect(self) -> dict[str, Any]:
            if self.name not in kept:
                raise DockerException(["container", "inspect", self.name], 1, f"Error: No such container: {self.name}\n")
            return {"Config": {"Labels": {"botbox.run": f"token-of-{self.name}"}}}

        async def remove(self) -> None:
            kept.discard(self.name)
            removals.append(f"container:{self.name}")

    class FakeVolume:
        def __init__(self, name: str) -> None:
            self.name = name

        async def remove(self) -> None:
            removals.append(f"volume:{self.name}")

    with (
        patch("port_codebase.port_codebase.Container", FakeContainer),
        patch("port_codebase.port_codebase.Volume", FakeVolume),
    ):
        yield removals


@pytest.fixture(autouse=True)
def box(kept: set[str]) -> Iterator[type[FakeBotbox]]:
    fake = type("Box", (FakeBotbox,), {"boxes": [], "runs": [], "kept": kept})
    with patch("port_codebase.port_codebase.Botbox", fake):
        yield fake
