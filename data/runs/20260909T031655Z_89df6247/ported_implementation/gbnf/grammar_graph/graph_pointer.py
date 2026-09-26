from .colorize import colorize
from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


class GraphPointer:
    def __init__(self, node, parent=None):
        if node is None:
            raise Exception("Node is undefined")
        self.node = node
        self.parent = parent
        self._valid = None
        self.id = f"{parent.id}-{node.id}" if parent is not None else node.id

    def resolve(self, resolved: bool = False):
        """
        1. If the current node is an end node, and the pointer has a parent, return the
           parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_
           resolved is true, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none
           exists, throw an error.
        """
        if is_graph_pointer_rule_ref(self):
            if resolved:
                if self.node.next is None:
                    raise Exception(f"No next node: {self.node!r}")
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in self.node.rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_graph_pointer_rule_end(self):
            if self.parent is None:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_graph_pointer_rule_char(self) or is_graph_pointer_rule_char_exclude(
            self
        ):
            yield self
        else:
            raise Exception(f"Unknown rule: {self.node.rule!r}")

    def fetch_next(self):
        # if this pointer is invalid, then we don't return any new pointers
        if self._valid is False:
            return

        # if this pointer is an end node, we return the parent's next node. If no parent
        # exists, we return nothing, since it's the end of the line.
        if is_rule_end(self.node.rule):
            if self.parent is not None:
                yield from self.parent.fetch_next()
        else:
            if self.node.next is None:
                raise Exception(f"No next node: {self.node!r}")
            yield from GraphPointer(self.node.next, self.parent).resolve()

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, valid: bool):
        self._valid = valid

    def print(self, colorize=colorize) -> str:
        return print_graph_pointer(self, colorize)

    def __repr__(self) -> str:
        return self.print(colorize=colorize)
