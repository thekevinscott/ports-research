from __future__ import annotations

from typing import Sequence

__all__ = ["is_point_in_range", "isPointInRange"]


def is_point_in_range(point: int, rng: Sequence[int]) -> bool:
    start, end = rng[0], rng[1]
    return point >= start and point <= end


isPointInRange = is_point_in_range
