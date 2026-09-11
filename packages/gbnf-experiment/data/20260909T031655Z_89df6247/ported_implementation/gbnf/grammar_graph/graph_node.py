from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta, next=None):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next
        self._id = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, pointers=None, show_position=False, colorize=colorize) -> str:
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(colorize=colorize, show_position=False)
