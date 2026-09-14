from collections.abc import Iterator

from tree_sitter import Node

from .languages import LanguageSpec


def named_nodes(root: Node, *, prune: frozenset[str] = frozenset()) -> Iterator[tuple[Node, int]]:
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        yield node, depth
        stack.extend(
            (child, depth + 1) for child in reversed(node.named_children) if child.type not in prune
        )


def measure_function(function: Node, spec: LanguageSpec) -> dict:
    branches = sum(spec.is_branch(node) for node, _ in named_nodes(function, prune=spec.functions))
    return {
        "lines": function.end_point.row - function.start_point.row + 1,
        "cyclomatic": 1 + branches,
    }


def measure_tree(root: Node, spec: LanguageSpec) -> dict:
    nodes = list(named_nodes(root))
    return {
        "node_count": len(nodes),
        "max_depth": max(depth for _, depth in nodes),
        "functions": [measure_function(node, spec) for node, _ in nodes if node.type in spec.functions],
    }
