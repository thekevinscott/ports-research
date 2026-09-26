from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Union

from .colorize import Color, Colorize
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer


def print_graph_pointer(pointer: 'GraphPointer') -> Callable[..., str]:
    def _print(colorize: Colorize) -> str:
        return colorize(f'*{get_parent_stack_id(pointer, colorize)}', Color.RED)

    return _print


def print_graph_node(node: 'GraphNode') -> Callable[..., str]:
    def _print(colorize: Colorize, pointers=None, show_position: bool = False) -> str:
        col = colorize
        rule = node.rule

        parts: List[str] = []
        if show_position:
            parts.extend([
                col('{', Color.BLUE),
                col(node.id, Color.GRAY),
                col('}', Color.BLUE),
            ])
        if is_rule_char(rule):
            values: List[str] = []
            for v in rule.value:
                if is_range(v):
                    # the reference maps a range to an array, which stringifies
                    # with a comma between its two entries
                    values.append(','.join(col(chr(val), Color.YELLOW) for val in v))
                else:
                    values.append(get_char(v))
            parts.extend([
                col('[', Color.GRAY),
                col(''.join(values), Color.YELLOW),
                col(']', Color.GRAY),
            ])
        elif is_rule_ref(rule):
            parts.append(
                col('Ref(', Color.GRAY) + col(f'{rule.value}', Color.GREEN) + col(')', Color.GRAY)
            )
        else:
            parts.append(col(rule.type, Color.YELLOW))

        if pointers:
            for pointer in pointers:
                pointer_parts: List[str] = []
                if pointer.node is node:
                    pointer_parts.append(pointer.print(colorize=col))
                if pointer_parts:
                    parts.append(col('[', Color.GRAY))
                    parts.extend(pointer_parts)
                    parts.append(col(']', Color.GRAY))

        pieces = [''.join(parts)]
        if node.next is not None:
            pieces.append(node.next.print(
                colorize=col,
                pointers=pointers,
                show_position=show_position,
            ))
        return col('-> ', Color.GRAY).join(piece for piece in pieces if piece)

    return _print


def get_char(char_code: int) -> str:
    char = chr(char_code)
    if char == '\n':
        return '\\n'
    return char
