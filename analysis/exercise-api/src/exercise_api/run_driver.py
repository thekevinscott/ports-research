import json
import os
import resource
import subprocess
import tempfile
from pathlib import Path

from .driver_command import driver_command

DRIVER_FAILED = {"ok": False, "error_type": "driver_failed", "error_pos": None, "rules": None, "elapsed_ns": None}
DRIVER_EXIT = {"ok": False, "error_type": "driver_exit", "error_pos": None, "rules": None, "elapsed_ns": None}


def run_driver(
    *,
    language: str,
    target: Path,
    cases: list[dict],
    adapt: bool,
    timeout: float,
    memory_limit_bytes: int,
    repeat: int = 1,
    warmup: int = 0,
) -> list[dict]:
    command = driver_command(language=language, target=target, adapt=adapt, repeat=repeat, warmup=warmup)
    payload = "".join(json.dumps(case) + "\n" for case in cases)
    with tempfile.TemporaryDirectory() as scratch:
        try:
            process = subprocess.run(
                command,
                input=payload,
                capture_output=True,
                text=True,
                cwd=scratch,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                timeout=timeout,
                preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes)),
            )
        except subprocess.TimeoutExpired:
            return [DRIVER_FAILED] * len(cases)
    if process.returncode != 0:
        return [DRIVER_FAILED] * len(cases)
    results = [json.loads(line) for line in process.stdout.splitlines() if line.strip()][: len(cases)]
    return results + [DRIVER_EXIT] * (len(cases) - len(results))
