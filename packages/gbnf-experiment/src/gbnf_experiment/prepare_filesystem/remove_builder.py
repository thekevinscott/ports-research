import shutil
from pathlib import Path

from .strip_builder_reexports import strip_builder_reexports

BUILDER_DIRECTORIES = {"typescript": "src/builder"}


def remove_builder(*, directory: Path, language: str) -> None:
    """Delete the language's grammar-authoring DSL from beside the library being ported.

    The typescript reference ships src/builder/, a template-literal DSL for building
    GBNF grammars programmatically. Python has no counterpart: gbnf/rules_builder/ is
    parser internals, not an authoring surface. Porting src/builder/ in either direction
    has no target, so the container is not shown it.
    """
    builder = BUILDER_DIRECTORIES.get(language)
    if not builder or not (directory / builder).is_dir():
        return
    shutil.rmtree(directory / builder)
    strip_builder_reexports(directory / "src" / "index.ts")
