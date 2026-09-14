from pathlib import Path


def discover_modules(source_dir: Path) -> list[Path]:
    """Every non-package, non-test Python module under `source_dir`, sorted by path."""
    return sorted(
        path
        for path in source_dir.rglob("*.py")
        if path.name != "__init__.py" and not path.name.endswith("_test.py")
    )
