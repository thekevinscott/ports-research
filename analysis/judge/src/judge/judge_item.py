import json
import os
import subprocess
import time
from tempfile import TemporaryDirectory

from judge.parse_output import parse_output


def judge_item(prompt: str, *, schema: dict, model: str, effort: str) -> dict:
    """One non-interactive claude call on subscription auth, tools off, output held to the schema."""
    command = [
        "claude", "-p",
        "--output-format", "json",
        "--json-schema", json.dumps(schema),
        "--tools", "",
        "--model", model,
        "--effort", effort,
        # No CLAUDE.md, memory, hooks, plugins or MCP servers: the judge sees the prompt alone.
        "--safe-mode",
        "--no-session-persistence",
    ]
    env = {key: value for key, value in os.environ.items() if key != "ANTHROPIC_API_KEY"}
    started = time.monotonic()
    with TemporaryDirectory() as cwd:
        process = subprocess.run(command, input=prompt, capture_output=True, text=True, env=env, cwd=cwd)
    wall_seconds = round(time.monotonic() - started, 1)
    if process.returncode != 0:
        raise RuntimeError(f"claude exited {process.returncode}: {process.stderr.strip() or process.stdout.strip()}")
    return {**parse_output(process.stdout), "wall_seconds": wall_seconds}
