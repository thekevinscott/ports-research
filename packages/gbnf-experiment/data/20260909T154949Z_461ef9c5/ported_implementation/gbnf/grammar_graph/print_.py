"""Port of ``src/grammar-graph/print.ts``."""
from __future__ import annotations

from typing import List, Union

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .type_guards import is_range, is_rule_char, is_rule_ref


def print_graph_pointer(pointer, colorize) -> str:
    return colorize(f'*{get_parent_stack_id(pointer, colorize)}', Color.RED)


def _get_char(char_code: int) -> str:
    char = chr(char_code)
    return '\\n' if char == '\n' else char


def print_graph_node(node, pointers=None, show_position: bool = False, colorize=None) -> str:
    col = colorize
    rule = node.rule

    parts: List[Union[str, int]] = []
    if show_position:
        parts.extend([
            col('{', Color.BLUE),
            col(node.id, Color.GRAY),
            col('}', Color.BLUE),
        ])
    if is_rule_char(rule):
        rendered = ''.join(
            ''.join(col(chr(val), Color.YELLOW) for val in v) if is_range(v)
            else _get_char(v)
            for v in rule.value
        )
        parts.extend([
            col('[', Color.GRAY),
            col(rendered, Color.YELLOW),
            col(']', Color.GRAY),
        ])
    elif is_rule_ref(rule):
        parts.append(
            col('Ref(', Color.GRAY) + col(f'{rule.value}', Color.GREEN) + col(')', Color.GRAY))
    else:
        parts.append(col(rule.type.value, Color.YELLOW))

    if pointers:
        for pointer in pointers:
            pointer_parts: List[str] = []
            if pointer.node is node:
                pointer_parts.append(print_graph_pointer(pointer, col))
            if pointer_parts:
                parts.append(col('[', Color.GRAY))
                parts.extend(pointer_parts)
                parts.append(col(']', Color.GRAY))

    rendered_parts = [''.join(str(part) for part in parts)]
    if node.next is not None:
        rendered_parts.append(
            print_graph_node(
                node.next, pointers=pointers, show_position=show_position, colorize=col))
    return col('-> ', Color.GRAY).join(part for part in rendered_parts if part)
