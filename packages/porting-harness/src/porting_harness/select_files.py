from collections.abc import Sequence
from pathlib import Path

import pathspec


def select_files(*, paths: Sequence[str | Path], patterns: Sequence[str]) -> list[Path]:
    """The paths the patterns name, relative and sorted.

    Default deny, gitignore syntax: a positive pattern includes, a `!` pattern
    excludes, and anything unnamed is never returned. paths is a listing of
    files relative to one root; nothing here touches a filesystem.
    """
    spec = pathspec.PathSpec.from_lines("gitignore", patterns)
    return sorted(
        Path(path) for path in paths if spec.match_file(Path(path).as_posix())
    )
