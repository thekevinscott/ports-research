from __future__ import annotations

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer, col) -> str:
    return col(f"*{get_parent_stack_id(pointer, col)}", Color.RED)


def print_graph_node(node, col, pointers=None, show_position: bool = False) -> str:
    rule = node.rule

    parts: list[str] = []
    if show_position:
        parts.extend(
            [
                col("{", Color.BLUE),
                col(node.id, Color.GRAY),
                col("}", Color.BLUE),
            ]
        )
    if is_rule_char(rule):
        parts.extend(
            [
                col("[", Color.GRAY),
                col(
                    "".join(
                        "".join(col(chr(val), Color.YELLOW) for val in v)
                        if is_range(v)
                        else _get_char(v)
                        for v in rule.value
                    ),
                    Color.YELLOW,
                ),
                col("]", Color.GRAY),
            ]
        )
    elif is_rule_ref(rule):
        parts.append(
            col("Ref(", Color.GRAY) + col(f"{rule.value}", Color.GREEN) + col(")", Color.GRAY)
        )
    else:
        parts.append(col(rule.type, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: list[str] = []
            if pointer.node is node:
                pointer_parts.append(print_graph_pointer(pointer, col))
            if pointer_parts:
                parts.append(col("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col("]", Color.GRAY))

    rest = (
        node.next.print(col=col, pointers=pointers, show_position=show_position)
        if node.next is not None
        else None
    )
    return col("-> ", Color.GRAY).join(part for part in ["".join(parts), rest] if part)


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
