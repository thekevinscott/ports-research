from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer, colorize=None, **_kwargs) -> str:
    col = colorize
    return col(f"*{get_parent_stack_id(pointer, col)}", Color.RED)


def print_graph_node(node, colorize=None, pointers=None, show_position=False) -> str:
    col = colorize
    rule = node.rule

    parts = []
    if show_position:
        parts.extend(
            [
                col("{", Color.BLUE),
                col(node.id, Color.GRAY),
                col("}", Color.BLUE),
            ]
        )

    if is_rule_char(rule):
        rendered = []
        for v in rule.value:
            if is_range(v):
                rendered.append("".join(col(chr(val), Color.YELLOW) for val in v))
            else:
                rendered.append(_get_char(v))
        parts.extend(
            [
                col("[", Color.GRAY),
                col("".join(rendered), Color.YELLOW),
                col("]", Color.GRAY),
            ]
        )
    elif is_rule_ref(rule):
        parts.append(
            col("Ref(", Color.GRAY)
            + col(f"{rule.value}", Color.GREEN)
            + col(")", Color.GRAY)
        )
    else:
        parts.append(col(rule.type, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts = []
            if pointer.node is node:
                pointer_parts.append(pointer.print(colorize=col))
            if pointer_parts:
                parts.append(col("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col("]", Color.GRAY))

    pieces = ["".join(parts)]
    if node.next is not None:
        rendered_next = node.next.print(
            pointers=pointers, colorize=col, show_position=show_position
        )
        if rendered_next:
            pieces.append(rendered_next)
    return col("-> ", Color.GRAY).join(pieces)


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
