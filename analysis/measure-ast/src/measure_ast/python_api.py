from tree_sitter import Node

from measure_ast.function_signature import arity, text
from measure_ast.label import label


def unwrap(node: Node) -> Node:
    return node.child_by_field_name("definition") if node.type == "decorated_definition" else node


def class_arity(statement: Node, definition: Node) -> int:
    """__init__'s parameters without self; else a dataclass's annotated fields; else 0."""
    body = [unwrap(child) for child in definition.child_by_field_name("body").named_children]
    for member in body:
        if member.type == "function_definition" and text(member.child_by_field_name("name")) == "__init__":
            return arity(member) - 1
    decorators = [text(d) for d in statement.named_children if d.type == "decorator"]
    if not any("dataclass" in d for d in decorators):
        return 0
    assignments = [m.named_children[0] for m in body if m.type == "expression_statement" and m.named_children]
    return sum(a.type == "assignment" and a.child_by_field_name("type") is not None for a in assignments)


def dunder_all(statement: Node) -> list[str]:
    assignment = statement.named_children[0] if statement.type == "expression_statement" else None
    if assignment is None or assignment.type != "assignment":
        return []
    left, right = assignment.child_by_field_name("left"), assignment.child_by_field_name("right")
    if text(left) != "__all__" or right is None or right.type not in ("list", "tuple"):
        return []
    return [text(s.named_children[1]) for s in right.named_children if s.type == "string" and len(s.named_children) == 3]


def python_api(roots: list[Node]) -> set[str]:
    """Public top-level defs and classes with arity, plus every name in __all__."""
    declared: list[tuple[str, int]] = []
    listed: list[str] = []
    for root in roots:
        for statement in root.named_children:
            definition = unwrap(statement)
            if definition.type == "function_definition":
                declared.append((text(definition.child_by_field_name("name")), arity(definition)))
            elif definition.type == "class_definition":
                declared.append((text(definition.child_by_field_name("name")), class_arity(statement, definition)))
            else:
                listed.extend(dunder_all(statement))
    arities = dict(reversed(declared))
    public = {label(name, n) for name, n in declared if not name.startswith("_")}
    return public | {label(name, arities.get(name)) for name in listed}
