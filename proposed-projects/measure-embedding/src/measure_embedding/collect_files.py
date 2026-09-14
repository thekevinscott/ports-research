import os
from collections.abc import Collection
from pathlib import Path

from .excluded import excluded


def collect_files(target: Path, *, suffixes: Collection[str], exclude: list[str]) -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if not excluded(d, exclude)]
        for name in filenames:
            path = Path(dirpath, name)
            if path.suffix in suffixes and not excluded(path.relative_to(target).as_posix(), exclude):
                found.append(path)
    return sorted(found)
