import subprocess
from pathlib import Path

PRETTIER_VERSION = "3.6.2"
FORMATTERS = {
    "python": (["ruff", "format"], ["ruff", "check", "--select", "I", "--fix"]),
    "typescript": (["pnpm", "dlx", f"prettier@{PRETTIER_VERSION}", "--write"],),
}


def refused(argv: list[str], files: list[Path]) -> list[Path]:
    if subprocess.run([*argv, *(str(f) for f in files)], capture_output=True).returncode == 0:
        return []
    return [f for f in files if subprocess.run([*argv, str(f)], capture_output=True).returncode != 0]


def format_tree(language: str, root: Path, files: list[Path]) -> list[str]:
    if not files:
        return []
    failed = {path for argv in FORMATTERS[language] for path in refused(argv, files)}
    return sorted(path.relative_to(root).as_posix() for path in failed)
