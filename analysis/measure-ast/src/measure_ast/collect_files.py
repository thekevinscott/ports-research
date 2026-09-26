import os
from collections.abc import Collection
from fnmatch import fnmatch
from pathlib import Path


def excluded(path: str, exclude: list[str]) -> bool:
    candidates = [path, *Path(path).parts]
    return any(fnmatch(c, pattern) for pattern in exclude for c in candidates)


def collect_files(target: Path, *, suffixes: Collection[str], exclude: list[str]) -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if not excluded(d, exclude)]
        for name in filenames:
            path = Path(dirpath, name)
            if path.suffix in suffixes and not excluded(path.relative_to(target).as_posix(), exclude):
                found.append(path)
    return sorted(found)
