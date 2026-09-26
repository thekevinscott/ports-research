from fnmatch import fnmatch
from pathlib import Path


def excluded(path: str, exclude: list[str]) -> bool:
    candidates = [path, *Path(path).parts]
    return any(fnmatch(c, pattern) for pattern in exclude for c in candidates)
