from __future__ import annotations

from typing import Sequence


def is_point_in_range(point: int, range_: Sequence[int]) -> bool:
    start, end = range_[0], range_[1]
    return start <= point <= end
