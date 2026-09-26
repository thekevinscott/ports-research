from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Union

from .colorize import Color, Colorize, colorize as default_colorize
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer
    from .types import Pointers

__all__ = ["print_graph_pointer", "print_graph_node", "printGraphPointer", "printGraphNode"]


def print_graph_pointer(pointer: "GraphPointer") -> Callable[..., str]:
    def _print(colorize: Colorize = default_colorize, **_kwargs) -> str:
        return colorize(f"*{get_parent_stack_id(pointer, colorize)}", Color.RED)

    return _print


def print_graph_node(node: "GraphNode") -> Callable[..., str]:
    def _print(
        pointers: Optional["Pointers"] = None,
        show_position: bool = False,
        colorize: Colorize = default_colorize,
    ) -> str:
        col = colorize
        rule = node.rule

        parts: List[str] = []
        if show_position:
            parts.extend([
                col("{", Color.BLUE),
                col(node.id, Color.GRAY),
                col("}", Color.BLUE),
            ])

        if is_rule_char(rule):
            values: List[str] = []
            for value in rule.value:
                if is_range(value):
                    # JS joins a nested array with `,` via Array.prototype.toString
                    values.append(",".join(col(chr(val), Color.YELLOW) for val in value))
                else:
                    values.append(get_char(value))
            parts.extend([
                col("[", Color.GRAY),
                col("".join(values), Color.YELLOW),
                col("]", Color.GRAY),
            ])
        elif is_rule_ref(rule):
            parts.append(col("Ref(", Color.GRAY) + col(f"{rule.value}", Color.GREEN) + col(")", Color.GRAY))
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

        next_view = (
            node.next.print(pointers=pointers, colorize=col, show_position=show_position)
            if node.next is not None
            else None
        )
        return col("-> ", Color.GRAY).join([part for part in ["".join(parts), next_view] if part])

    return _print


def get_char(char_code: Union[int, float]) -> str:
    char = chr(int(char_code))
    if char == "\n":
        return "\\n"
    return char


printGraphPointer = print_graph_pointer
printGraphNode = print_graph_node
