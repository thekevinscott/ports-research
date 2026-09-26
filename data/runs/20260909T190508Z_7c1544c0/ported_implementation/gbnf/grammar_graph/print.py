from typing import Any, Callable, List, Optional, Union

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer: Any) -> Callable[..., str]:
    def print_(colorize: Callable[..., str]) -> str:
        return colorize(f'*{get_parent_stack_id(pointer, colorize)}', Color.RED)

    return print_


def print_graph_node(node: Any) -> Callable[..., str]:
    def print_(
        colorize: Callable[..., str],
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ) -> str:
        rule = node.rule
        col = colorize

        parts: List[Union[str, int]] = []
        if show_position:
            parts.extend([
                col('{', Color.BLUE),
                col(node.id, Color.GRAY),
                col('}', Color.BLUE),
            ])
        if is_rule_char(rule):
            values = []
            for v in rule.value:
                if is_range(v):
                    values.append(''.join(col(chr(val), Color.YELLOW) for val in v))
                else:
                    values.append(_get_char(v))
            parts.extend([
                col('[', Color.GRAY),
                col(''.join(values), Color.YELLOW),
                col(']', Color.GRAY),
            ])
        elif is_rule_ref(rule):
            parts.append(
                col('Ref(', Color.GRAY)
                + col(f'{rule.value}', Color.GREEN)
                + col(')', Color.GRAY)
            )
        else:
            parts.append(col(rule.type.value, Color.YELLOW))

        if pointers:
            for pointer in pointers:
                pointer_parts: List[str] = []
                if pointer.node is node:
                    pointer_parts.append(pointer.print(colorize=col))
                if pointer_parts:
                    parts.append(col('[', Color.GRAY))
                    parts.extend(pointer_parts)
                    parts.append(col(']', Color.GRAY))

        rendered = [''.join(str(part) for part in parts)]
        if node.next is not None:
            rendered.append(
                node.next.print(
                    colorize=col, pointers=pointers, show_position=show_position
                )
            )
        return col('-> ', Color.GRAY).join(part for part in rendered if part)

    return print_


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == '\n':
        return '\\n'
    return char
