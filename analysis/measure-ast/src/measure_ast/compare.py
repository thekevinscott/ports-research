from pathlib import Path
from statistics import fmean, median

from measure_ast.extract_functions import FunctionRecord, extract_functions
from measure_ast.label import label
from measure_ast.languages import LANGUAGES
from measure_ast.measure_ast import measure_ast
from measure_ast.pair_functions import pair_functions
from measure_ast.parse_files import parse_files
from measure_ast.python_api import python_api
from measure_ast.tree_edit_distance import tree_edit_distance
from measure_ast.typescript_api import typescript_api
from measure_ast.wasserstein import wasserstein

API_SURFACE = {"python": python_api, "typescript": typescript_api}


def side(language: str, target: Path, exclude: list[str]) -> tuple[dict, list[FunctionRecord], set[str]]:
    roots = [tree.root_node for tree in parse_files(language=language, target=target, exclude=exclude)]
    functions = [record for root in roots for record in extract_functions(root, LANGUAGES[language])]
    return measure_ast(language=language, target=target, exclude=exclude), functions, API_SURFACE[language](roots)


def matched_pair(port: FunctionRecord, reference: FunctionRecord) -> dict:
    distance = tree_edit_distance(port.tree, reference.tree)
    return {
        "port": label(port.name, port.arity),
        "reference": label(reference.name, reference.arity),
        "port_lines": port.lines,
        "reference_lines": reference.lines,
        "tree_edit_distance": distance,
        "normalised": distance / max(port.size, reference.size),
    }


def compare(*, language: str, port: Path, reference: Path, exclude: list[str]) -> dict:
    port_measures, port_functions, port_api = side(language, port, exclude)
    reference_measures, reference_functions, reference_api = side(language, reference, exclude)
    named_reference = [fn for fn in reference_functions if fn.name is not None]
    pairs, port_only, reference_only = pair_functions(
        [fn for fn in port_functions if fn.name is not None], named_reference
    )
    matched = [matched_pair(p, r) for p, r in pairs]
    normalised = [pair["normalised"] for pair in matched]
    port_cyclomatic = sorted(fn.cyclomatic for fn in port_functions)
    reference_cyclomatic = sorted(fn.cyclomatic for fn in reference_functions)
    return {
        "language": language,
        "port": str(port),
        "reference": str(reference),
        "delta": {
            field: {"delta": value - reference_measures[field], "port": value, "reference": reference_measures[field]}
            for field, value in port_measures.items()
            if field not in ("language", "target")
        },
        "functions": {
            "matched_count": len(matched),
            "port_only_count": len(port_only),
            "reference_only_count": len(reference_only),
            "matched": matched,
            "port_only": sorted(label(fn.name, fn.arity) for fn in port_only),
            "reference_only": sorted(label(fn.name, fn.arity) for fn in reference_only),
            "matched_fraction": len(matched) / len(named_reference) if named_reference else None,
            "median_line_drift": median(p["port_lines"] - p["reference_lines"] for p in matched) if matched else None,
        },
        "tree_edit_distance": {
            "mean_normalised": fmean(normalised) if normalised else None,
            "median_normalised": median(normalised) if normalised else None,
        },
        "branching": {
            "port": port_cyclomatic,
            "reference": reference_cyclomatic,
            "wasserstein": wasserstein(port_cyclomatic, reference_cyclomatic)
            if port_cyclomatic and reference_cyclomatic
            else None,
        },
        "api_surface": {
            "shared": sorted(port_api & reference_api),
            "port_only": sorted(port_api - reference_api),
            "reference_only": sorted(reference_api - port_api),
        },
    }
