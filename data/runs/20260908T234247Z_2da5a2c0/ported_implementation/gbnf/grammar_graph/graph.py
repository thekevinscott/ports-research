"""Port of ``src/grammar-graph/graph.ts``."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..utils.errors.input_parse_error import InputParseError
from ..utils.is_point_in_range import is_point_in_range
from .colorize import Color, colorize
from .generic_set import GenericSet
from .get_input_as_code_points import get_input_as_code_points
from .get_serialized_rule_key import get_serialized_rule_key
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer
from .rule_ref import RuleRef
from .type_guards import (
    is_range,
    is_rule_char,
    is_rule_char_excluded,
    is_rule_end,
    is_rule_ref,
)
from .types import ValidInput

RootNode = Dict[int, GraphNode]
Pointers = GenericSet[GraphPointer, str]


def _make_pointers() -> Pointers:
    return GenericSet(lambda p: p.id)


class Graph:
    def __init__(
        self,
        grammar: str,
        stacked_rules: List[List[List[Any]]],
        root_id: int,
    ) -> None:
        self.grammar = grammar
        self._roots: Dict[int, RootNode] = {}
        self._previous_code_points: List[int] = []

        rule_refs: List[RuleRef] = []
        unique_rules: GenericSet[Any, str] = GenericSet(get_serialized_rule_key)
        for stack_id in range(len(stacked_rules)):
            stack = stacked_rules[stack_id]
            if stack is None:
                raise ValueError(f"No rules defined for stack: {stack_id}")
            nodes: RootNode = {}
            for path_id in range(len(stack)):
                path = stack[path_id]
                node: Optional[GraphNode] = None
                for step_id in range(len(path) - 1, -1, -1):
                    next = node
                    rule = stack[path_id][step_id]
                    unique_rules.add(rule)
                    if is_rule_ref(rule):
                        rule_refs.append(rule)
                    # rules coming in may be identical but have different references.
                    # here, we ensure we always use the same reference for an identical
                    # rule. this makes future comparisons easier.
                    unique_rule = unique_rules.get(rule)
                    if unique_rule is None:
                        raise ValueError("Could not get unique rule")
                    node = GraphNode(
                        unique_rule, GraphNodeMeta(stack_id, path_id, step_id), next
                    )
                if node is None:
                    raise ValueError("Could not get node")
                nodes[path_id] = node

            self._roots[stack_id] = nodes

        root_node = self._roots.get(root_id)
        if not root_node:
            raise ValueError(f"Root node not found for value: {root_id}")
        self._root_node: RootNode = root_node

        for rule_ref in rule_refs:
            rule_ref.nodes = list(self._get_root_node(rule_ref.value).values())

    def _get_root_node(self, value: int) -> RootNode:
        root_node = self._roots.get(value)
        if not root_node:
            raise ValueError(f"Root node not found for value: {value}")
        return root_node

    def _get_initial_pointers(self) -> Pointers:
        pointers = _make_pointers()

        root_node = self._root_node
        if not root_node:
            raise ValueError("Root node is not defined")

        for node, parent in self._fetch_nodes_for_root_node(root_node):
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
                        break
                    if is_range(possible_code_point):
                        valid = is_point_in_range(code_point, possible_code_point)
                    else:
                        valid = code_point == possible_code_point
                self._set_valid(graph_pointers, valid)
            elif is_rule_char_excluded(rule):
                valid = True
                for possible_code_point in rule.value:
                    if not valid:
                        break
                    if is_range(possible_code_point):
                        valid = not is_point_in_range(code_point, possible_code_point)
                    else:
                        valid = code_point != possible_code_point
                self._set_valid(graph_pointers, valid)
            elif not is_rule_end(rule):
                raise ValueError(f"Unsupported rule: {rule!r}")

        # a pointer's id is the sum of its node's id and its parent's id chain.
        # if two pointers share the same id, it means they point to the same node and
        # have identical parent chains. for the purposes of walking the graph, we only
        # need to keep one of them.
        next_pointers = _make_pointers()
        for current_pointer in current_pointers:
            for unresolved_next_pointer in current_pointer.fetch_next():
                for resolved_next_pointer in self._resolve_pointer(unresolved_next_pointer):
                    next_pointers.add(resolved_next_pointer)
        return next_pointers

    def _resolve_pointer(self, unresolved_pointer: GraphPointer) -> Iterator[GraphPointer]:
        for resolved_pointer in unresolved_pointer.resolve():
            if is_rule_ref(resolved_pointer.node.rule):
                raise ValueError(
                    "Encountered a reference rule when building pointers to the graph"
                )
            if is_rule_end(resolved_pointer.node.rule) and resolved_pointer.parent:
                raise ValueError(
                    "Encountered an ending rule with a parent when building pointers to the graph"
                )
            yield resolved_pointer

    def add(self, src: ValidInput, _pointers: Optional[Pointers] = None) -> Pointers:
        pointers = _pointers if _pointers is not None else self._get_initial_pointers()
        code_points = get_input_as_code_points(src)
        for code_point_pos in range(len(code_points)):
            code_point = code_points[code_point_pos]
            pointers = self._parse(pointers, code_point)
            if pointers.size == 0:
                raise InputParseError(
                    code_points, code_point_pos, list(self._previous_code_points)
                )
        self._previous_code_points.extend(code_points)
        return pointers

    def _fetch_nodes_for_root_node(
        self,
        root_nodes: RootNode,
        parent: Optional[GraphPointer] = None,
    ) -> Iterator[Tuple[GraphNode, Optional[GraphPointer]]]:
        """Yield either the node, or if a reference rule, the referenced node.

        This is distinct from the logic in ``GraphPointer`` because that needs a rule
        ref with already-defined nodes; this function is used to _set_ those nodes.
        """
        for node in list(root_nodes.values()):
            if is_rule_ref(node.rule):
                yield from self._fetch_nodes_for_root_node(
                    self._get_root_node(node.rule.value), GraphPointer(node, parent)
                )
            else:
                yield (node, parent)

    def print(
        self,
        pointers: Optional[Pointers] = None,
        colors: bool = False,
    ) -> str:
        col: Callable[[Union[str, int], Color], str] = (
            colorize if colors else (lambda s, _color: f"{s}")
        )
        nodes: List[List[GraphNode]] = [
            list(node_map.values()) for node_map in self._roots.values()
        ]
        graph_view: List[str] = []
        for root_node in nodes:
            for node in root_node:
                graph_view.append(
                    node.print(pointers=pointers, show_position=True, colorize=col)
                )
        return "\n" + "\n".join(graph_view)

    def __repr__(self) -> str:
        return self.print(colors=True)

    def _iterate_over_pointers(
        self, pointers: Pointers
    ) -> Iterator[Tuple[Any, List[GraphPointer]]]:
        seen_rules: Dict[Any, List[GraphPointer]] = {}
        for pointer in pointers:
            rule = pointer.rule
            if is_rule_ref(rule):
                raise ValueError(
                    "Encountered a reference rule in the graph, this should not happen"
                )
            seen_rule = seen_rules.get(rule)
            if seen_rule is None:
                seen_rule = [pointer]
                seen_rules[rule] = seen_rule
            else:
                seen_rule.append(pointer)

        for rule, graph_pointers in seen_rules.items():
            yield (rule, graph_pointers)
