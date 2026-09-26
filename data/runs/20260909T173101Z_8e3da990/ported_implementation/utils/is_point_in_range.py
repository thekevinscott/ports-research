from collections.abc import Sequence


def is_point_in_range(point: float, range_: Sequence[float]) -> bool:
    start, end = range_[0], range_[1]
    return point >= start and point <= end


isPointInRange = is_point_in_range
