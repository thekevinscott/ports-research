from tree_sitter import Node

NOT_PARAMETERS = frozenset({"comment", "keyword_separator", "positional_separator"})


def text(node: Node) -> str:
    return node.text.decode()


def function_name(function: Node) -> str | None:
    """The function's own name, else the binding it is assigned to; None for a callback."""
    name = function.child_by_field_name("name")
    if name is not None:
        return text(name)
    parent = function.parent
    match parent.type:
        case "variable_declarator" | "public_field_definition":
            binding = parent.child_by_field_name("name")
        case "pair":
            binding = parent.child_by_field_name("key")
        case "assignment_expression":
            binding = parent.child_by_field_name("left")
            if binding.type == "member_expression":
                binding = binding.child_by_field_name("property")
        case _:
            return None
    return text(binding)


def arity(function: Node) -> int:
    parameters = function.child_by_field_name("parameters")
    if parameters is None:
        return int(function.child_by_field_name("parameter") is not None)
    return sum(child.type not in NOT_PARAMETERS for child in parameters.named_children)
