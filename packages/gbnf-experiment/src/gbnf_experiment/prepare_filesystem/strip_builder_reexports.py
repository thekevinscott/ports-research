import re
from pathlib import Path

BUILDER_REEXPORT = re.compile(r"export\b[^;]*?from\s+['\"]\./builder/[^'\"]*['\"];")


def strip_builder_reexports(index_ts: Path) -> None:
    """Delete index.ts's re-exports of the removed builder DSL.

    Left in place, `export * from "./builder/index.js"` and the ToStringArgs
    re-export point at a directory that no longer exists, and the reference
    fails to typecheck.
    """
    if not index_ts.is_file():
        return
    text = index_ts.read_text()
    stripped = re.sub(r"\n{3,}", "\n\n", BUILDER_REEXPORT.sub("", text))
    if stripped != text:
        index_ts.write_text(stripped)
