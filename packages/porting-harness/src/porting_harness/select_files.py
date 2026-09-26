from collections.abc import Sequence

import pathspec


def select_files(*, paths: Sequence[str], patterns: Sequence[str]) -> list[str]:
    """The paths the patterns name, sorted.

    Default deny, gitignore syntax: a positive pattern includes, a `!` pattern
    excludes, and anything unnamed is never returned. paths is a listing of
    posix paths relative to one root; nothing here touches a filesystem.
    """
    spec = pathspec.PathSpec.from_lines("gitignore", patterns)
    return sorted(path for path in paths if spec.match_file(path))
