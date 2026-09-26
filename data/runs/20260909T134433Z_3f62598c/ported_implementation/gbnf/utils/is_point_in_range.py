from typing import Sequence


def is_point_in_range(point: int, rng: Sequence[int]) -> bool:
    start, end = rng[0], rng[1]
    return point >= start and point <= end
