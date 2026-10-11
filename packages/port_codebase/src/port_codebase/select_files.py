from collections.abc import Sequence
from pathlib import Path

import pathspec


def select_files(*, source: Path, patterns: Sequence[str]) -> list[Path]:
    """The files under source that the patterns name, relative and sorted.

    Default deny, gitignore syntax: a positive pattern includes, a `!` pattern
    excludes, and anything unnamed is never returned. Symlinks are neither
    returned nor descended into: they name a path the patterns did not.
    """
    spec = pathspec.PathSpec.from_lines("gitignore", patterns)
    selected: list[Path] = []
    for path in source.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(source)
        if spec.match_file(relative.as_posix()):
            selected.append(relative)
    return sorted(selected)
