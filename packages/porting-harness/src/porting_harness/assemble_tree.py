import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pathspec


@dataclass(frozen=True)
class AssemblyReport:
    patterns: tuple[str, ...]
    included: tuple[str, ...]
    excluded: tuple[str, ...]


def assemble_tree(
    *, source: Path, destination: Path, patterns: Sequence[str]
) -> AssemblyReport:
    """Copy source into destination, admitting only the files a pattern names.

    Default deny, gitignore syntax: a positive pattern includes, a `!` pattern
    excludes, and anything unnamed never reaches the destination. Symlinks are
    neither copied nor descended into: they name a path the patterns did not.
    """
    spec = pathspec.PathSpec.from_lines("gitignore", patterns)
    included: list[str] = []
    excluded: list[str] = []
    for path in source.rglob("*"):
        relative = path.relative_to(source).as_posix()
        if path.is_symlink():
            excluded.append(relative)
            continue
        if not path.is_file():
            continue
        if not spec.match_file(relative):
            excluded.append(relative)
            continue
        included.append(relative)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return AssemblyReport(
        patterns=tuple(patterns),
        included=tuple(sorted(included)),
        excluded=tuple(sorted(excluded)),
    )
