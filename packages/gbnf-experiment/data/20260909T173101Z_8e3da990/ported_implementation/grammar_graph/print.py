from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from .colorize import Color, colorize as default_colorize
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer: Any, colorize: Callable[..., str] = default_colorize) -> str:
    return colorize(f'*{get_parent_stack_id(pointer, colorize)}', Color.RED)


def print_graph_node(
    node: Any,
    pointers: Any = None,
    show_position: bool = False,
    colorize: Callable[..., str] = default_colorize,
) -> str:
    col = colorize
    # the chain of `next` nodes is walked iteratively; it is as long as the rule
    # is, which can outrun Python's recursion limit.
    return col('-> ', Color.GRAY).join(
        _print_single_graph_node(current, pointers, show_position, col)
        for current in _iterate_nodes(node)
    )


def _iterate_nodes(node: Any) -> Any:
    while node:
        yield node
        node = node.next


def _print_single_graph_node(
    node: Any,
    pointers: Any,
    show_position: bool,
    col: Callable[..., str],
) -> str:
    rule = node.rule

    parts: list[str] = []
    if show_position:
        parts.extend([
            col('{', Color.BLUE),
            col(node.id, Color.GRAY),
            col('}', Color.BLUE),
        ])
    if is_rule_char(rule):
        parts.extend([
            col('[', Color.GRAY),
            col(''.join(
                # a nested array joins with commas on its way into the string
                ','.join(col(_from_char_code(val), Color.YELLOW) for val in value)
                if is_range(value) else _get_char(value)
                for value in rule.value
            ), Color.YELLOW),
            col(']', Color.GRAY),
        ])
    elif is_rule_ref(rule):
        parts.append(col('Ref(', Color.GRAY) + col(f'{rule.value}', Color.GREEN) + col(')', Color.GRAY))
    else:
        parts.append(col(rule.type, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: list[str] = []
            if pointer.node is node:
                pointer_parts.append(print_graph_pointer(pointer, colorize=col))
            if pointer_parts:
                parts.append(col('[', Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col(']', Color.GRAY))

    return ''.join(parts)


def _from_char_code(char_code: float) -> str:
    """`String.fromCharCode`: the code is coerced to a 16 bit unsigned integer."""
    if isinstance(char_code, float) and math.isnan(char_code):
        return '\0'
    return chr(int(char_code) % 0x10000)


def _get_char(char_code: float) -> str:
    char = _from_char_code(char_code)
    if char == '\n':
        return '\\n'
    return char


# JS-name aliases for parity with the reference implementation.
printGraphPointer = print_graph_pointer
printGraphNode = print_graph_node
