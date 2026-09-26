from .colorize import colorize
from .print import print_graph_node


class GraphNode:
    def __init__(self, rule, meta, next_=None):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id = None

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = (
                f"{self.meta['stackId']},{self.meta['pathId']},{self.meta['stepId']}"
            )
        return self._id

    def print(self, pointers=None, show_position=False, colorize=colorize):
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(colorize=lambda s, c: f"{s}", show_position=False)
