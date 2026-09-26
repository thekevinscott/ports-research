from typing import TYPE_CHECKING, Callable, List, Optional, Union

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref

if TYPE_CHECKING:
    from .generic_set import GenericSet
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer

Colorize = Callable[[Union[str, int], Color], str]


def print_graph_pointer(pointer: "GraphPointer", colorize: Colorize) -> str:
    return colorize(f"*{get_parent_stack_id(pointer, colorize)}", Color.RED)


def print_graph_node(
    node: "GraphNode",
    colorize: Colorize,
    pointers: Optional["GenericSet"] = None,
    show_position: bool = False,
) -> str:
    rule = node.rule

    parts: List[str] = []
    if show_position:
        parts.extend(
            [
                colorize("{", Color.BLUE),
                colorize(node.id, Color.GRAY),
                colorize("}", Color.BLUE),
            ]
        )
    if is_rule_char(rule):
        parts.extend(
            [
                colorize("[", Color.GRAY),
                colorize(
                    "".join(
                        # a range prints its bounds comma separated, matching the way
                        # the reference implementation stringifies a nested array
                        ",".join(colorize(chr(val), Color.YELLOW) for val in v)
                        if is_range(v)
                        else get_char(v)
                        for v in rule.value
                    ),
                    Color.YELLOW,
                ),
                colorize("]", Color.GRAY),
            ]
        )
    elif is_rule_ref(rule):
        parts.append(
            colorize("Ref(", Color.GRAY)
            + colorize(f"{rule.value}", Color.GREEN)
            + colorize(")", Color.GRAY)
        )
    else:
        parts.append(colorize(rule.type, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: List[str] = []
            if pointer.node is node:
                pointer_parts.append(pointer.print(colorize=colorize))
            if pointer_parts:
                parts.append(colorize("[", Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(colorize("]", Color.GRAY))

    return colorize("-> ", Color.GRAY).join(
        part
        for part in [
            "".join(parts),
            node.next.print(
                pointers=pointers, colorize=colorize, show_position=show_position
            )
            if node.next
            else None,
        ]
        if part
    )


def get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
