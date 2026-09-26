from typing import TYPE_CHECKING, Callable, List

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .grammar_graph_types import PrintOpts
from .type_guards import is_range, is_rule_char, is_rule_ref

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer


def get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char


def print_graph_pointer(pointer: "GraphPointer") -> Callable[[PrintOpts], str]:
    def print_pointer(opts: PrintOpts) -> str:
        col = opts.colorize
        return col(f"*{get_parent_stack_id(pointer, col)}", Color.RED)

    return print_pointer


def print_graph_node(node: "GraphNode") -> Callable[[PrintOpts], str]:
    def print_node(opts: PrintOpts) -> str:
        pointers = opts.pointers
        col = opts.colorize
        show_position = opts.show_position
        rule = node.rule
        parts: List[str] = []
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
                            "".join(col(get_char(val), Color.YELLOW) for val in v)
                            if is_range(v)
                            else get_char(v)
                            for v in rule.value
                        ),
                        Color.YELLOW,
                    ),
                    col("]", Color.GRAY),
                ]
            )
        elif is_rule_ref(rule):
            parts.extend(
                [
                    col("Ref(", Color.GRAY),
                    col(rule.value, Color.GREEN),
                    col(")", Color.GRAY),
                ]
            )
        else:
            parts.append(col(rule.type, Color.YELLOW))

        if pointers is not None and pointers.size > 0:
            for pointer in pointers:
                pointer_parts: List[str] = []
                if pointer.node is node:
                    pointer_parts.append(pointer.print(opts))

                if len(pointer_parts) > 0:
                    parts.extend(
                        [
                            col("[", Color.GRAY),
                            col("".join(pointer_parts), Color.YELLOW),
                            col("]", Color.GRAY),
                        ]
                    )

        parts_to_return = ["".join(parts)]
        if node.next:
            parts_to_return.append(node.next.print(opts))

        return col("-> ", Color.GRAY).join(parts_to_return)

    return print_node
