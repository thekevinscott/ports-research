from __future__ import annotations

from typing import Dict, Iterator, List, Optional, Tuple

from ..utils.errors import InputParseError
from ..utils.is_point_in_range import is_point_in_range
from .colorize import colorize
from .get_input_as_code_points import get_input_as_code_points
from .get_serialized_rule_key import get_serialized_rule_key
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer
from .pointers import Pointers
from .type_guards import (
    is_range,
    is_rule_char,
    is_rule_char_exclude,
    is_rule_end,
    is_rule_ref,
)
from .types import PrintOpts, ValidInput

# The nodes of a single stack, keyed by path id.
RootNode = List[GraphNode]


class Graph:
    def __init__(self, grammar: str, stacked_rules, root_id: int):
        self.grammar = grammar
        self.previous_code_points: List[int] = []
        self._roots: Dict[int, RootNode] = {}
        rule_refs = []
        unique_rules: Dict[str, object] = {}

        for stack_id in range(len(stacked_rules)):
            stack = stacked_rules[stack_id]
            nodes: RootNode = []
            for path_id in range(len(stack)):
                path = stack[path_id]
                node: Optional[GraphNode] = None
                for step_id in range(len(path) - 1, -1, -1):
                    next_node = node
                    rule = path[step_id]
                    key = get_serialized_rule_key(rule)
                    # rules coming in may be identical but have different references.
                    # here, we ensure we always use the same reference for an identical rule.
                    # this makes future comparisons easier.
                    if key not in unique_rules:
                        unique_rules[key] = rule
                        if is_rule_ref(rule):
                            rule_refs.append(rule)
                    unique_rule = unique_rules.get(key)
                    if unique_rule is None:
                        raise ValueError('Could not get unique rule')
                    node = GraphNode(
                        unique_rule,
                        GraphNodeMeta(stack_id, path_id, step_id),
                        next_node,
                    )

                if node is None:
                    raise ValueError('Could not get node')
                nodes.append(node)
            self._roots[stack_id] = nodes

        root_node = self._roots.get(root_id)
        if root_node is None:
            raise ValueError(f'Root node not found for value: {root_id}')
        self._root_node = root_node

        for rule_ref in rule_refs:
            rule_ref.nodes = self._get_root_node(rule_ref.value)

    def _get_root_node(self, value: int) -> RootNode:
        root_node = self._roots.get(value)
        if root_node is None:
            raise ValueError(f'Root node not found for value: {value}')
        return root_node

    def _get_initial_pointers(self) -> Pointers:
        pointers = Pointers()

        for node, parent in self._fetch_nodes_for_root_node(self._root_node):
            pointer = GraphPointer(node, parent)
            for resolved_pointer in self._resolve_pointer(pointer):
                pointers.add(resolved_pointer)
        return pointers

    def _set_valid(self, pointers: List[GraphPointer], valid: bool) -> None:
        for pointer in pointers:
            pointer.valid = valid

    def _parse(self, current_pointers: Pointers, code_point: int) -> Pointers:
        for rule, graph_pointers in self._iterate_over_pointers(current_pointers):
            if is_rule_char(rule):
                valid = False
                for possible_code_point in rule.value:
                    if valid:
                        continue
                    if is_range(possible_code_point):
                        if is_point_in_range(code_point, possible_code_point):
                            valid = True
                    elif code_point == possible_code_point:
                        valid = True
                self._set_valid(graph_pointers, valid)
            elif is_rule_char_exclude(rule):
                valid = True
                for possible_code_point in rule.value:
                    if not valid:
                        continue
                    if is_range(possible_code_point):
                        if is_point_in_range(code_point, possible_code_point):
                            valid = False
                    elif code_point == possible_code_point:
                        valid = False
                self._set_valid(graph_pointers, valid)
            elif not is_rule_end(rule):
                raise ValueError(f'Unsupported rule: {rule!r}')

        # a pointer's id is the sum of its node's id and its parent's id chain.
        # if two pointers share the same id, it means they point to the same node and have
        # identical parent chains.
        # for the purposes of walking the graph, we only need to keep one of them.
        next_pointers = Pointers()
        for current_pointer in current_pointers:
            for unresolved_next_pointer in current_pointer.fetch_next():
                for resolved_next_pointer in self._resolve_pointer(
                    unresolved_next_pointer
                ):
                    next_pointers.add(resolved_next_pointer)
        return next_pointers

    def _resolve_pointer(
        self, unresolved_pointer: GraphPointer
    ) -> Iterator[GraphPointer]:
        for resolved_pointer in unresolved_pointer.resolve():
            if is_rule_ref(resolved_pointer.node.rule):
                raise ValueError(
                    'Encountered a reference rule when building pointers to the graph'
                )
            if (
                is_rule_end(resolved_pointer.node.rule)
                and resolved_pointer.parent is not None
            ):
                raise ValueError(
                    'Encountered an ending rule with a parent when building pointers to the graph'
                )
            yield resolved_pointer

    def add(self, src: ValidInput, pointers: Optional[Pointers] = None) -> Pointers:
        if not isinstance(src, str):
            raise TypeError('src must be a string in graph.add')
        current_pointers = pointers if pointers is not None else self._get_initial_pointers()

        code_points = get_input_as_code_points(src)

        for code_point_pos in range(len(code_points)):
            current_pointers = self._parse(
                current_pointers, code_points[code_point_pos]
            )
            if current_pointers.size == 0:
                raise InputParseError(
                    code_points, code_point_pos, list(self.previous_code_points)
                )
        self.previous_code_points.extend(code_points)
        return current_pointers

    # generator that yields either the node, or if a reference rule, the referenced node
    # we need this function, as distinct from leveraging the logic in GraphPointer,
    # because that needs a rule ref with already defined nodes; this function is used to _set_
    # those nodes
    def _fetch_nodes_for_root_node(
        self,
        root_nodes: RootNode,
        parent: Optional[GraphPointer] = None,
    ) -> Iterator[Tuple[GraphNode, Optional[GraphPointer]]]:
        for node in root_nodes:
            rule = node.rule
            if is_rule_ref(rule):
                yield from self._fetch_nodes_for_root_node(
                    self._get_root_node(rule.value),
                    GraphPointer(node, parent),
                )
            else:
                yield (node, parent)

    def print(self, pointers: Optional[Pointers] = None, colors: bool = False) -> str:
        if pointers is None:
            pointers = Pointers()
        graph_view: List[str] = []
        for root_node in self._roots.values():
            for node in root_node:
                graph_view.append(
                    node.print(
                        PrintOpts(
                            pointers=pointers,
                            show_position=True,
                            colorize=colorize
                            if colors
                            else (lambda text, color: f'{text}'),
                        )
                    )
                )

        return '\n'.join(graph_view)

    def _iterate_over_pointers(
        self, pointers: Pointers
    ) -> Iterator[Tuple[object, List[GraphPointer]]]:
        # Rules are deduplicated by reference when the graph is built, so grouping by
        # identity groups every pointer that sits on the same rule.
        seen_rules: Dict[int, Tuple[object, List[GraphPointer]]] = {}
        for pointer in pointers:
            rule = pointer.rule
            if is_rule_ref(rule):
                raise ValueError('Encountered a reference rule in the graph')

            seen_rule = seen_rules.get(id(rule))
            if seen_rule is None:
                seen_rules[id(rule)] = (rule, [pointer])
            else:
                seen_rule[1].append(pointer)

        yield from seen_rules.values()
