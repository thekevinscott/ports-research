from pathlib import Path

_METADATA_FILES = ("pyproject.toml", "README.md", "package.json", "Makefile")


def rename_library(tree_root: Path, old_name: str, new_name: str) -> None:
    """Renames the library directory and rewrites its name in project metadata files.

    This is plain text substitution, not a codemod: `pyproject.toml`, `README.md`,
    `package.json`, and `Makefile` are prose and config, not code with import
    semantics, so there is no reference graph for a refactoring tool to resolve here.
    """
    old_directory = tree_root / old_name
    if old_directory.is_dir():
        old_directory.rename(tree_root / new_name)
    for filename in _METADATA_FILES:
        metadata_file = tree_root / filename
        if metadata_file.is_file():
            metadata_file.write_text(metadata_file.read_text().replace(old_name, new_name))
