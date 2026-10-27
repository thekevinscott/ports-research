"""Integration tests: Botbox faked where port_codebase imports it."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from botbox import RunResult


class FakeBotbox:
    """What port_codebase asked the box for, and what the run prints."""

    boxes: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    stdout = ""
    exit_code = 0

    def __init__(self, agent: Any, *, dockerfile: Path | None = None, allow: tuple[str, ...] = ()) -> None:
        self.boxes.append({"agent": agent, "dockerfile": dockerfile, "allow": allow})

    async def __aenter__(self) -> "FakeBotbox":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        return None

    async def run(self, command: str, *, mounts: Any = (), workdir: str | None = None, output: Path) -> RunResult:
        self.runs.append({"command": command, "mounts": mounts, "workdir": workdir, "output": output})
        output.mkdir(parents=True, exist_ok=True)
        (output / "stdout.txt").write_text(self.stdout)
        return RunResult(exit_code=self.exit_code)


@pytest.fixture(autouse=True)
def box() -> Iterator[type[FakeBotbox]]:
    fake = type("Box", (FakeBotbox,), {"boxes": [], "runs": []})
    with patch("port_codebase.port_codebase.Botbox", fake):
        yield fake
