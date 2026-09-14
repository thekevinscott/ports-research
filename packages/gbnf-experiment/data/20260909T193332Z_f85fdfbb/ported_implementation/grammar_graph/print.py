from __future__ import annotations

from .colorize import Color, colorize as default_colorize
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer, colorize=default_colorize) -> str:
    col = colorize
    return col(f"*{get_parent_stack_id(pointer, col)}", Color.RED)


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char


def print_graph_node(
    node,
    pointers=None,
    show_position: bool = False,
    colorize=default_colorize,
) -> str:
    col = colorize
    rule = node.rule

    parts: list[str] = []
    if show_position:
        parts.append(col("{", Color.BLUE))
        parts.append(col(node.id, Color.GRAY))
        parts.append(col("}", Color.BLUE))

    if is_rule_char(rule):
        rendered = []
        for v in rule.value:
            if is_range(v):
                # A nested array stringifies with commas between its members.
                rendered.append(",".join(col(chr(val), Color.YELLOW) for val in v))
            else:
                rendered.append(_get_char(v))
        parts.append(col("[", Color.GRAY))
        parts.append(col("".join(rendered), Color.YELLOW))
        parts.append(col("]", Color.GRAY))
    elif is_rule_ref(rule):
        parts.append(
            col("Ref(", Color.GRAY)
            + col(f"{rule.value}", Color.GREEN)
            + col(")", Color.GRAY)
        )
    else:
        parts.append(col(str(rule.type), Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: list[str] = []
            if pointer.node is node:
                pointer_parts.append(pointer.print(colorize=col))
            if pointer_parts:
                parts.append(col("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col("]", Color.GRAY))

    tail = (
        node.next.print(pointers=pointers, colorize=col, show_position=show_position)
        if node.next is not None
        else None
    )
    return col("-> ", Color.GRAY).join(p for p in ["".join(parts), tail] if p)
