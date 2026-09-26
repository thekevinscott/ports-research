from pathlib import Path

from measure_embedding.strip_comments import strip_comments

from .collect_files import collect_files
from .format_tree import format_tree
from .languages import LANGUAGES


def without_blank_lines(source: bytes) -> bytes:
    return b"".join(line + b"\n" for line in source.splitlines() if line.strip())


def normalize_tree(*, language: str, source: Path, destination: Path, exclude: list[str]) -> dict:
    files = collect_files(source, suffixes=LANGUAGES[language].parsers, exclude=exclude)
    if not files:
        raise FileNotFoundError(f"no {language} source files under {source}")
    copies = []
    for path in files:
        copy = destination / path.relative_to(source)
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(without_blank_lines(strip_comments(path.read_bytes(), language)))
        copies.append(copy)
    formatter_failures = format_tree(language, destination, copies)
    return {
        "paths": [copy.relative_to(destination).as_posix() for copy in copies],
        "lines": sum(len(copy.read_bytes().splitlines()) for copy in copies),
        "formatter_failures": formatter_failures,
    }
