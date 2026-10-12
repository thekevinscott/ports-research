from pathlib import Path
from statistics import fmean

from measure_ast.languages import LANGUAGES
from measure_ast.measure_tree import measure_tree
from measure_ast.parse_files import parse_files


def measure_ast(*, language: str, target: Path, exclude: list[str]) -> dict:
    spec = LANGUAGES[language]
    trees = [measure_tree(tree.root_node, spec) for tree in parse_files(language=language, target=target, exclude=exclude)]
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
