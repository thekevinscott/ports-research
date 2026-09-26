from typing import Callable, List, Union

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def _identity(text: Union[str, int], color: str) -> str:
    return f"{text}"


def print_graph_pointer(
    pointer, colorize: Callable[[Union[str, int], str], str] = _identity, **_opts
) -> str:
    col = colorize
    return col(f"*{get_parent_stack_id(pointer, col)}", Color.RED)


def print_graph_node(
    node,
    pointers=None,
    colorize: Callable[[Union[str, int], str], str] = _identity,
    show_position: bool = False,
) -> str:
    pointers = list(pointers) if pointers is not None else []
    col = colorize
    rule = node.rule
    parts: List[str] = []
    if show_position:
        parts += [col("{", Color.BLUE), col(node.id, Color.GRAY), col("}", Color.BLUE)]

    if is_rule_char(rule):
        parts += [
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
    elif is_rule_ref(rule):
        parts += [
            col("Ref(", Color.GRAY),
            col(rule.value, Color.GREEN),
            col(")", Color.GRAY),
        ]
    else:
        # `type` lives only in the rule's `__dict__` property, so this raises an
        # AttributeError for RuleEnd and RuleCharExclude.
        parts.append(col(rule.type, Color.YELLOW))

    for pointer in pointers:
        pointer_parts: List[str] = []
        if pointer.node is node:
            pointer_parts.append(
                pointer.print(colorize=colorize, show_position=show_position)
            )

        if pointer_parts:
            parts += [
                col("[", Color.GRAY),
                col("".join(pointer_parts), Color.YELLOW),
                col("]", Color.GRAY),
            ]

    parts_to_return = ["".join(parts)]
    if node.next:
        parts_to_return.append(
            node.next.print(
                pointers=pointers, colorize=colorize, show_position=show_position
            )
        )

    return col("-> ", Color.GRAY).join(parts_to_return)


def get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
