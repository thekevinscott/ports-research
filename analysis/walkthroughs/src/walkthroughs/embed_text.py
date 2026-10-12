import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

GENERATE_EMBEDDING_DIR = Path(__file__).resolve().parents[3] / "generate-embedding"
# The notebook's embedding model: analysis/notebook/src/Codebase.py EMBEDDING_MODEL.
MODEL = "qwen3-embedding-0.6b-q8_0"


def embed_text(text: str, *, url: str) -> list[float]:
    """Embed one text through the generate-embedding CLI against the server at url."""
    with TemporaryDirectory() as directory:
        path = Path(directory) / "step.txt"
        path.write_text(text)
        process = subprocess.run(
            ["uv", "run", "--directory", str(GENERATE_EMBEDDING_DIR), "generate-embedding", str(path), "--model", MODEL],
            capture_output=True,
            text=True,
            env={**os.environ, "GENERATE_EMBEDDING_BASE_URL": url},
        )
    if process.returncode != 0:
        raise RuntimeError(f"generate-embedding failed (exit {process.returncode}): {process.stderr.strip()}")
    return json.loads(process.stdout)["embedding"]
