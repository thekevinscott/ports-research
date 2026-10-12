from fnmatch import fnmatch
from pathlib import Path

# The notebook's exclude list (analysis/notebook/src/corpus.py), with its typescript extras
# builder/ and dev/ applied to every tree: the experiment never shipped them as source.
EXCLUDE = [
    "node_modules",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    "dist",
    "dev-deps",
    "tests",
    "test",
    "integration-tests",
    "conftest.py",
    "*_test.py",
    "test_*.py",
    "*.test.ts",
    "*.spec.ts",
    "builder",
    "dev",
    # Build and lint configuration, not library code.
    "*.config.*",
    ".*",
]
SUFFIXES = {".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs"}


def source_files(root: Path) -> list[Path]:
    """The library's source files under root, relative and sorted: code only, no tests."""

    def excluded(relative: Path) -> bool:
        return any(fnmatch(part, pattern) for pattern in EXCLUDE for part in relative.parts)

    relatives = (path.relative_to(root) for path in root.rglob("*") if path.is_file())
    return sorted(r for r in relatives if r.suffix in SUFFIXES and not excluded(r))
