import subprocess
from pathlib import Path

GENERATE_EMBEDDING_DIR = Path(__file__).resolve().parents[4] / "packages" / "generate-embedding"


def run_generate_embedding(source: Path, output: Path, *, model: str) -> None:
    process = subprocess.run(
        [
            "uv", "run", "--directory", str(GENERATE_EMBEDDING_DIR),
            "generate-embedding", str(source), "--model", model, "--output", str(output),
        ],
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"generate-embedding {source} failed (exit {process.returncode}): {process.stderr}"
        )
