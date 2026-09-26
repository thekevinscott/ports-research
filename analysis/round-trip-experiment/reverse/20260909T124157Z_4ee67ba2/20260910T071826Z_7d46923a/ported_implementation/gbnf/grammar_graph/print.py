from typing import Any, Callable, List, Optional

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer: Any) -> Callable[..., str]:
    def _print(
        colorize: Callable[..., str],
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ) -> str:
        return colorize(f"*{get_parent_stack_id(pointer, colorize)}", Color.RED)

    return _print


def print_graph_node(node: Any) -> Callable[..., str]:
    def _print(
        colorize: Callable[..., str],
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ) -> str:
        col = colorize
        rule = node.rule
        parts: List[str] = []
        if show_position:
            parts.extend(
                [col("{", Color.BLUE), col(node.id, Color.GRAY), col("}", Color.BLUE)]
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

        if pointers is not None and len(pointers) > 0:
            for pointer in pointers:
                pointer_parts: List[str] = []
                if pointer.node is node:
                    pointer_parts.append(
                        pointer.print(
                            colorize=colorize,
                            pointers=pointers,
                            show_position=show_position,
                        )
                    )

                if len(pointer_parts) > 0:
                    parts.extend(
                        [
                            col("[", Color.GRAY),
                            col("".join(pointer_parts), Color.YELLOW),
                            col("]", Color.GRAY),
                        ]
                    )

        parts_to_return: List[str] = ["".join(parts)]
        if node.next:
            parts_to_return.append(
                node.next.print(
                    colorize=colorize, pointers=pointers, show_position=show_position
                )
            )

        return col("-> ", Color.GRAY).join(parts_to_return)

    return _print


def get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == "\n":
        return "\\n"
    return char
