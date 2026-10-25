"""A reference's own test commands run in the box, unmodified, from a writable copy.

Real containers, no model: the agent here is a shell command, so nothing is billed.

The tree mirrors what tripped agents in the gbnf runs: an ESM package whose
`vitest.config.ts` imports `vitest/config`, and a python package whose tests are
run as `python -m pytest` as often as `pytest`.
"""

import json
from pathlib import Path

import pytest
from botbox import ClaudeAgent

from port_codebase import port_codebase

JAVASCRIPT = {
    "package.json": json.dumps({"name": "reference", "type": "module"}),
    "vitest.config.ts": (
        "import { defineConfig } from 'vitest/config';\n"
        "export default defineConfig({ test: { include: ['src/**/*.test.ts'] } });\n"
    ),
    "src/add.ts": "export const add = (a: number, b: number): number => a + b;\n",
    "src/add.test.ts": (
        "import { expect, test } from 'vitest';\n"
        "import { add } from './add';\n"
        "test('adds', () => { expect(add(2, 3)).toBe(5); });\n"
    ),
}
PYTHON = {
    "pyproject.toml": (
        '[project]\nname = "reference"\nversion = "0"\nrequires-python = ">=3.14"\n'
        '[tool.pytest.ini_options]\npython_files = ["*_test.py"]\n'
    ),
    "reference/__init__.py": "def add(a, b):\n    return a + b\n",
    "reference/add_test.py": (
        "from reference import add\n\n\ndef describe_add():\n"
        "    def it_adds():\n        assert add(2, 3) == 5\n"
    ),
}
COMMANDS = {
    "vitest run": "cp -r /input/javascript /tmp/javascript && cd /tmp/javascript && vitest run",
    "pytest": "cp -r /input/python /tmp/python && cd /tmp/python && pytest -q",
    "python -m pytest": "cp -r /input/python /tmp/python && cd /tmp/python && python -m pytest -q",
}


class Shell:
    """An agent that ignores the prompt and runs one shell command in the box."""

    image = ClaudeAgent.image
    dockerfile = ClaudeAgent.dockerfile
    home = ClaudeAgent.home
    transcripts = ClaudeAgent.transcripts
    allow: tuple[str, ...] = ()

    def __init__(self, command: str) -> None:
        self._command = command

    def stage_auth(self, home: Path) -> None:
        pass

    def command(self, prompt: str) -> str:
        return self._command


def write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


@pytest.fixture
def reference(tmp_path: Path) -> Path:
    write(tmp_path / "source" / "javascript", JAVASCRIPT)
    write(tmp_path / "source" / "python", PYTHON)
    return tmp_path / "source"


def describe_the_box():
    @pytest.mark.parametrize("name", list(COMMANDS))
    async def it_runs_the_references_own_test_command(reference, tmp_path, name):
        result = await port_codebase(
            agent=Shell(COMMANDS[name]),
            prompt="",
            source=reference,
            output=tmp_path / "output",
        )

        print(f"\n[box] {name}: exit={result.exit_code}\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}")
        assert result.exit_code == 0
        assert "1 passed" in result.stdout
