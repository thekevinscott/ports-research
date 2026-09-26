from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    __slots__ = ("rule", "next", "meta", "_id")

    def __init__(self, rule, meta: GraphNodeMeta, next_=None):
        self.rule = rule
        if meta is None:
            raise RuntimeError("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id = None

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, colorize_fn=colorize, pointers=None, show_position: bool = False):
        return print_graph_node(
            self, colorize_fn, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(colorize, show_position=False)

    def __hash__(self):
        return id(self)
