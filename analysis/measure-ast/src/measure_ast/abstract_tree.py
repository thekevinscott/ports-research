from tree_sitter import Node

from measure_ast.languages import LanguageSpec
from measure_ast.tree_edit_distance import LabelTree


def abstract(node: Node, spec: LanguageSpec) -> LabelTree:
    """Named nodes labelled by type alone; a literal is one leaf; comments are dropped."""
    if node.type in spec.literals:
        return (node.type, ())
    return (node.type, tuple(abstract(child, spec) for child in node.named_children if child.type != "comment"))
