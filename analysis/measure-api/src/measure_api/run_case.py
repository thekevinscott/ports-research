import json
import os
import signal
import subprocess
import sys
from pathlib import Path

DRIVERS = Path(__file__).resolve().parents[2] / "drivers"
TIMEOUT_SECONDS = 10
PREFIX_CAP = 16
TSX = "tsx@4.19.2"


def run_case(language: str, implementation: Path, grammar: str, text: str) -> dict:
    if language == "python":
        command = [sys.executable, str(DRIVERS / "driver.py")]
        env = {**os.environ, "PYTHONPATH": str(implementation), "PYTHONDONTWRITEBYTECODE": "1"}
    else:
        command = ["pnpm", "--silent", "dlx", TSX, str(DRIVERS / "driver.mts"), str(implementation / "src" / "index.ts")]
        env = dict(os.environ)
    # Its own session, so a timeout kills pnpm's node child along with pnpm.
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    # Chunks are code points, split here so both languages step through the same prefixes.
    case = {"grammar": grammar, "input": text, "chunks": list(text)[:PREFIX_CAP]}
    try:
        stdout, stderr = process.communicate(json.dumps(case), timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return {"steps": None, "crash": f"timed out after {TIMEOUT_SECONDS}s"}
    if process.returncode != 0 or not stdout.strip():
        return {"steps": None, "crash": stderr.strip() or f"exit {process.returncode} with no answer"}
    return {"steps": json.loads(stdout), "crash": None}
