from __future__ import annotations

from typing import NamedTuple

from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta(NamedTuple):
    stack_id: int
    path_id: int
    step_id: int

    # camelCase aliases, mirroring the reference API.
    @property
    def stackId(self) -> int:
        return self.stack_id

    @property
    def pathId(self) -> int:
        return self.path_id

    @property
    def stepId(self) -> int:
        return self.step_id


class GraphNode:
    """A single step in a rule path, linked to the step that follows it."""

    __slots__ = ("rule", "next", "meta", "_id")

    def __init__(self, rule, meta: GraphNodeMeta, next_=None):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id: str | None = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, pointers=None, show_position: bool = False, colorize=colorize) -> str:
        return print_graph_node(
            self,
            pointers=pointers,
            show_position=show_position,
            colorize=colorize,
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return self.print(show_position=False, colorize=lambda s, c: f"{s}")
