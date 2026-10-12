from pathlib import Path

from tree_sitter import Tree

from measure_ast.collect_files import collect_files
from measure_ast.languages import LANGUAGES


def parse_files(*, language: str, target: Path, exclude: list[str]) -> list[Tree]:
    spec = LANGUAGES[language]
    files = collect_files(target, suffixes=spec.parsers, exclude=exclude)
    if not files:
        raise FileNotFoundError(f"no {language} source files under {target}")
    return [spec.parsers[path.suffix].parse(path.read_bytes()) for path in files]
