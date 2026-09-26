from .print import print_graph_node


class GraphNodeMeta:
    def __init__(self, stack_id: int, path_id: int, step_id: int) -> None:
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta | None, next_node=None) -> None:
        self.rule = rule
        if not meta:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self._cached_id: str | None = None

    @property
    def id(self) -> str:
        if self._cached_id is None:
            self._cached_id = (
                f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
            )
        return self._cached_id

    def print(self, opts) -> str:
        return print_graph_node(self)(opts)

    def __repr__(self) -> str:
        return f"GraphNode(id={self.id!r}, rule={self.rule!r})"
