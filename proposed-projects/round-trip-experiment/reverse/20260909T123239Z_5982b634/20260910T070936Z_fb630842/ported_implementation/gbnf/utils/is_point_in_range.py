from __future__ import annotations

from ..grammar_graph.types import Range


def is_point_in_range(point: int, rng: Range) -> bool:
    start, end = rng
    if not isinstance(point, int) or isinstance(point, bool):
        raise TypeError('point must be an integer')
    return start <= point <= end
