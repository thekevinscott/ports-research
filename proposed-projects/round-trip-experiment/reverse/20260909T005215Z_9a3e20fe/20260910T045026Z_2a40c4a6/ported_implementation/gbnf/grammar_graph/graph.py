from typing import Iterator, Optional

from ..utils.errors import InputParseError
from ..utils.is_point_in_range import is_point_in_range
from .colorize import colorize
from .get_input_as_code_points import get_input_as_code_points
from .get_serialized_rule_key import get_serialized_rule_key
from .grammar_graph_types import PrintOpts, UnresolvedRule, ValidInput
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

# A root node maps a path id to the first node of that path.
RootNode = dict


class Graph:
    def __init__(
        self,
        grammar: str,
        stacked_rules: list[list[list[UnresolvedRule]]],
        root_id: int,
    ):
        self._roots: dict[int, RootNode] = {}
        self.grammar = grammar
        self.previous_code_points: list[int] = []
        rule_refs = []
        unique_rules: dict[str, UnresolvedRule] = {}

        for stack_id, stack in enumerate(stacked_rules):
            nodes: RootNode = {}
            for path_id, path in enumerate(stack):
                node: Optional[GraphNode] = None
                for step_id in range(len(path) - 1, -1, -1):
                    next_node = node
                    rule = stack[path_id][step_id]
                    unique_rules[get_serialized_rule_key(rule)] = rule
                    if is_rule_ref(rule):
                        rule_refs.append(rule)
                    # rules coming in may be identical but have different
                    # references. here, we ensure we always use the same
                    # reference for an identical rule. this makes future
                    # comparisons easier.
                    unique_rule = unique_rules.get(get_serialized_rule_key(rule))
                    if unique_rule is None:
                        raise ValueError("Could not get unique rule")
                    node = GraphNode(
                        unique_rule,
                        GraphNodeMeta(stack_id, path_id, step_id),
                        next_node,
                    )

                if node is None:
                    raise ValueError("Could not get node")
                nodes[path_id] = node
            self._roots[stack_id] = nodes

        root_node = self._roots.get(root_id)
        if root_node is None:
            raise ValueError(f"Root node not found for value: {root_id}")
        self._root_node = root_node

        for rule_ref in rule_refs:
            rule_ref.nodes = list(self.get_root_node(rule_ref.value).values())

    def get_root_node(self, value: int) -> RootNode:
        root_node = self._roots.get(value)
        if root_node is None:
            raise ValueError(f"Root node not found for value: {value}")
        return root_node

    def get_initial_pointers(self) -> Pointers:
        pointers = Pointers()

        root_node = self._root_node
        if root_node is None:
            raise ValueError("Root node is not defined")

        for node, parent in self.fetch_nodes_for_root_node(root_node):
            pointer = GraphPointer(node, parent)
            for resolved_pointer in self.resolve_pointer(pointer):
                pointers.add(resolved_pointer)
        return pointers

    def _set_valid(self, pointers: list[GraphPointer], valid: bool) -> None:
        for pointer in pointers:
            pointer.valid = valid

    def parse(self, current_pointers: Pointers, code_point: int) -> Pointers:
        for rule, graph_pointers in self.iterate_over_pointers(current_pointers):
            if is_rule_char(rule):
                valid = False
                for possible_code_point in rule.value:
                    if valid is True:
                        continue
                    elif is_range(possible_code_point):
                        if is_point_in_range(code_point, possible_code_point):
                            valid = True
                    elif code_point == possible_code_point:
                        valid = True
                self._set_valid(graph_pointers, valid)
            elif is_rule_char_exclude(rule):
                valid = True
                for possible_code_point in rule.value:
                    if valid is False:
                        continue
                    elif is_range(possible_code_point):
                        if is_point_in_range(code_point, possible_code_point):
                            valid = False
                    elif code_point == possible_code_point:
                        valid = False
                self._set_valid(graph_pointers, valid)
            elif not is_rule_end(rule):
                raise ValueError(f"Unsupported rule: {rule!r}")

        # a pointer's id is the sum of its node's id and its parent's id chain.
        # if two pointers share the same id, it means they point to the same
        # node and have identical parent chains. for the purposes of walking the
        # graph, we only need to keep one of them.
        next_pointers = Pointers()
        for current_pointer in current_pointers:
            for unresolved_next_pointer in current_pointer.fetch_next():
                for resolved_next_pointer in self.resolve_pointer(
                    unresolved_next_pointer
                ):
                    next_pointers.add(resolved_next_pointer)
        return next_pointers

    def resolve_pointer(
        self, unresolved_pointer: GraphPointer
    ) -> Iterator[GraphPointer]:
        for resolved_pointer in unresolved_pointer.resolve():
            if is_rule_ref(resolved_pointer.rule):
                raise ValueError(
                    "Encountered a reference rule when building pointers to the graph"
                )
            if is_rule_end(resolved_pointer.rule) and resolved_pointer.parent is not None:
                raise ValueError(
                    "Encountered an ending rule with a parent when building "
                    "pointers to the graph"
                )
            yield resolved_pointer

    def add(self, src: ValidInput, pointers: Optional[Pointers] = None) -> Pointers:
        if not isinstance(src, str):
            raise ValueError("src must be a string in graph.add")
        current_pointers = pointers if pointers is not None else self.get_initial_pointers()

        code_points = get_input_as_code_points(src)
        for code_point in code_points:
            if not isinstance(code_point, int) or isinstance(code_point, bool):
                raise ValueError("code_point must be an integer!")

        for code_point_pos, code_point in enumerate(code_points):
            current_pointers = self.parse(current_pointers, code_point)
            if len(current_pointers) == 0:
                raise InputParseError(
                    code_points, code_point_pos, list(self.previous_code_points)
                )
        self.previous_code_points.extend(code_points)
        return current_pointers

    def fetch_nodes_for_root_node(
        self,
        root_nodes: RootNode,
        parent: Optional[GraphPointer] = None,
    ) -> Iterator[tuple[GraphNode, Optional[GraphPointer]]]:
        """Yields either the node, or if a reference rule, the referenced node.

        We need this function, as distinct from leveraging the logic in
        GraphPointer, because that needs a rule ref with already defined nodes;
        this function is used to _set_ those nodes.
        """
        for node in list(root_nodes.values()):
            if is_rule_ref(node.rule):
                yield from self.fetch_nodes_for_root_node(
                    self.get_root_node(node.rule.value),
                    GraphPointer(node, parent),
                )
            else:
                yield node, parent

    def print(self, pointers: Optional[Pointers] = None, colors: bool = False) -> str:
        nodes = [list(root_node.values()) for root_node in self._roots.values()]
        resolved_pointers = pointers if pointers is not None else Pointers()
        graph_view: list[str] = []
        for root_node in nodes:
            for node in root_node:
                graph_view.append(
                    node.print(
                        PrintOpts(
                            colorize=colorize if colors else (lambda s, color: str(s)),
                            pointers=resolved_pointers,
                            show_position=True,
                        )
                    )
                )

        return "\n".join(graph_view)

    def iterate_over_pointers(
        self, pointers
    ) -> Iterator[tuple[UnresolvedRule, list[GraphPointer]]]:
        seen_rules: dict[int, tuple[UnresolvedRule, list[GraphPointer]]] = {}
        for pointer in pointers:
            rule = pointer.rule
            if is_rule_ref(rule):
                raise ValueError("Encountered a reference rule in the graph")

            seen_rule = seen_rules.get(id(rule))
            if seen_rule is None:
                seen_rule = (rule, [pointer])
                seen_rules[id(rule)] = seen_rule
            seen_rule[1].append(pointer)

        yield from seen_rules.values()
