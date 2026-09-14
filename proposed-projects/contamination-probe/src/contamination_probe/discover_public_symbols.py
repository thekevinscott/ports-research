import ast
from pathlib import Path

from .symbol_site import SymbolSite

_DEFINITION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def discover_public_symbols(source_dir: Path) -> list[SymbolSite]:
    """Every module-scope public definition under `source_dir`, sorted by path.

    Only module-scope names count: nested defs, method bodies, and anything starting
    with `_` are not part of the tree's public rename surface. `TypeVar(...)` and
    multi-target assignments are skipped rather than treated as renamable bindings.
    """
    sites: list[SymbolSite] = []
    for path in sorted(source_dir.rglob("*.py")):
        if path.name.endswith("_test.py"):
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in tree.body:
            if isinstance(node, _DEFINITION_NODES):
                if not node.name.startswith("_"):
                    sites.append(SymbolSite(path=path, lineno=node.lineno, name=node.name))
                continue
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                continue
            name = targets[0].id
            if name.startswith("_"):
                continue
            value = node.value
            if (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == "TypeVar"
            ):
                continue
            sites.append(SymbolSite(path=path, lineno=targets[0].lineno, name=name))
    return sites
