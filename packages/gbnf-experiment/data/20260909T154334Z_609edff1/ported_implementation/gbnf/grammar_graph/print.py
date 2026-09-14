from typing import Callable, List, Optional, Union

from .colorize import Color, colorize as default_colorize
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer, colorize: Callable = default_colorize) -> str:
    from .get_parent_stack_id import get_parent_stack_id

    return colorize(f"*{get_parent_stack_id(pointer, colorize)}", Color.RED)


def print_graph_node(
    node,
    pointers=None,
    show_position: bool = False,
    colorize: Callable = default_colorize,
) -> str:
    col = colorize
    rule = node.rule

    parts: List[Union[str, int]] = []
    if show_position:
        parts.extend(
            [
                col("{", Color.BLUE),
                col(node.id, Color.GRAY),
                col("}", Color.BLUE),
            ]
        )
    if is_rule_char(rule):
        printed_values = []
        for v in rule.value:
            if is_range(v):
                printed_values.append("".join(col(chr(val), Color.YELLOW) for val in v))
            else:
                printed_values.append(_get_char(v))
        parts.extend(
            [
                col("[", Color.GRAY),
                col("".join(printed_values), Color.YELLOW),
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

    if pointers is not None:
        for pointer in pointers:
            pointer_parts: List[str] = []
            if pointer.node is node:
                pointer_parts.append(pointer.print(colorize=col))
            if pointer_parts:
                parts.append(col("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col("]", Color.GRAY))

    next_printed: Optional[str] = (
        node.next.print(pointers=pointers, colorize=col, show_position=show_position)
        if node.next is not None
        else None
    )
    return col("-> ", Color.GRAY).join(
        part for part in ["".join(str(p) for p in parts), next_printed] if part
    )


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
