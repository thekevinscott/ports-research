from __future__ import annotations

from typing import Sequence


def is_point_in_range(point: int, given_range: Sequence[int]) -> bool:
    if not isinstance(point, int):
        raise ValueError("point must be an integer")
    return given_range[0] <= point <= given_range[1]
