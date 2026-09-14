from typing import Sequence


def is_point_in_range(point: int, point_range: Sequence[int]) -> bool:
    start, end = point_range
    return start <= point <= end
