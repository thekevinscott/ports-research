"""Port of ``src/grammar-graph/print.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer

Colorize = Callable[[Union[str, int], Color], str]


def print_graph_pointer(pointer: "GraphPointer", colorize: Colorize) -> str:
    return colorize(f"*{get_parent_stack_id(pointer, colorize)}", Color.RED)


def print_graph_node(
    node: "GraphNode",
    pointers: Optional[Any] = None,
    show_position: bool = False,
    colorize: Colorize = None,  # type: ignore[assignment]
) -> str:
    col = colorize
    rule = node.rule

    parts: List[str] = []
    if show_position:
        parts.append(col("{", Color.BLUE))
        parts.append(col(node.id, Color.GRAY))
        parts.append(col("}", Color.BLUE))
    if is_rule_char(rule):
        values: List[str] = []
        for v in rule.value:
            if is_range(v):
                # JS joins the outer array with '', which stringifies the inner
                # array with commas.
                values.append(",".join(col(chr(val), Color.YELLOW) for val in v))
            else:
                values.append(_get_char(v))
        parts.append(col("[", Color.GRAY))
        parts.append(col("".join(values), Color.YELLOW))
        parts.append(col("]", Color.GRAY))
    elif is_rule_ref(rule):
        parts.append(
            col("Ref(", Color.GRAY) + col(f"{rule.value}", Color.GREEN) + col(")", Color.GRAY)
        )
    else:
        parts.append(col(rule.type, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: List[str] = []
            if pointer.node is node:
                pointer_parts.append(pointer.print(colorize=col))
            if pointer_parts:
                parts.append(col("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col("]", Color.GRAY))

    next_printed = (
        node.next.print(pointers=pointers, colorize=col, show_position=show_position)
        if node.next is not None
        else None
    )
    return col("-> ", Color.GRAY).join(
        [part for part in ["".join(parts), next_printed] if part]
    )


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
