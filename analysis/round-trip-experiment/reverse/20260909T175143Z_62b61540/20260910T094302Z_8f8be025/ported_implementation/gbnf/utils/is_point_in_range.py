from ..grammar_graph.grammar_graph_types import Range


def is_point_in_range(point: int, range_: Range) -> bool:
    if not isinstance(point, int):
        raise ValueError("point must be an integer")
    return range_[0] <= point <= range_[1]
