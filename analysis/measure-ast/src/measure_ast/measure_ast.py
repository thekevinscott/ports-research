from pathlib import Path
from statistics import fmean

from .collect_files import collect_files
from .languages import LANGUAGES
from .measure_tree import measure_tree


def measure_ast(*, language: str, target: Path, exclude: list[str]) -> dict:
    spec = LANGUAGES[language]
    files = collect_files(target, suffixes=spec.parsers, exclude=exclude)
    if not files:
        raise FileNotFoundError(f"no {language} source files under {target}")
    trees = [
        measure_tree(spec.parsers[path.suffix].parse(path.read_bytes()).root_node, spec)
        for path in files
    ]
    lines = [fn["lines"] for tree in trees for fn in tree["functions"]]
    cyclomatic = [fn["cyclomatic"] for tree in trees for fn in tree["functions"]]
    return {
        "language": language,
        "target": str(target),
        "parsed_file_count": len(trees),
        "node_count": sum(tree["node_count"] for tree in trees),
        "max_depth": max(tree["max_depth"] for tree in trees),
        "function_count": len(lines),
        "mean_function_lines": fmean(lines) if lines else 0,
        "max_function_lines": max(lines, default=0),
        "mean_cyclomatic": fmean(cyclomatic) if cyclomatic else 0,
        "max_cyclomatic": max(cyclomatic, default=0),
    }
