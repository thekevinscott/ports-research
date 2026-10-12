from dataclasses import dataclass

from tree_sitter import Node

from measure_ast.abstract_tree import abstract
from measure_ast.function_signature import arity, function_name
from measure_ast.languages import LanguageSpec
from measure_ast.measure_tree import measure_function, named_nodes
from measure_ast.tree_edit_distance import LabelTree, tree_size


@dataclass(frozen=True)
class FunctionRecord:
    name: str | None
    arity: int
    lines: int
    cyclomatic: int
    tree: LabelTree
    size: int


def extract_functions(root: Node, spec: LanguageSpec) -> list[FunctionRecord]:
    records = []
    for node, _ in named_nodes(root):
        if node.type in spec.functions:
            tree = abstract(node, spec)
            records.append(
                FunctionRecord(function_name(node), arity(node), **measure_function(node, spec), tree=tree, size=tree_size(tree))
            )
    return records
