from typing import Sequence


def is_point_in_range(point: int, rng: Sequence[int]) -> bool:
    start, end = rng
    return start <= point <= end
