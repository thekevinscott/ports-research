import json
from collections.abc import Callable
from pathlib import Path

import numpy as np

from .collect_files import collect_files
from .embedded_text import embedded_text
from .run_generate_embedding import run_generate_embedding

SUFFIXES = {"python": {".py"}, "typescript": {".ts", ".tsx"}}


def stale(source: Path, vector: Path) -> bool:
    return not vector.is_file() or vector.stat().st_mtime_ns < source.stat().st_mtime_ns


def embed_codebase(
    *,
    language: str,
    target: Path,
    exclude: list[str],
    out: Path,
    model: str,
    strip_comments: bool = False,
    embed: Callable[..., None] = run_generate_embedding,
) -> dict:
    files = collect_files(target, suffixes=SUFFIXES[language], exclude=exclude)
    if not files:
        raise FileNotFoundError(f"no {language} source files under {target}")
    relative = [path.relative_to(target).as_posix() for path in files]
    embedded, lengths = 0, []
    for source, name in zip(files, relative):
        vector = out / f"{name}.npy"
        text = embedded_text(source, language, strip_comments)
        lengths.append(len(text.decode(errors="replace")))
        if not stale(source, vector):
            continue
        vector.parent.mkdir(parents=True, exist_ok=True)
        input_path = source
        if strip_comments:
            input_path = out / f"{name}.stripped"
            input_path.write_bytes(text)
        embed(input_path, vector, model=model)
        embedded += 1
    index = {
        "language": language,
        "target": str(target),
        "model": model,
        "dims": int(np.load(out / f"{relative[0]}.npy").shape[0]),
        "files": relative,
        "lengths": lengths,
    }
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return {**index, "embedded": embedded, "skipped": len(files) - embedded}
