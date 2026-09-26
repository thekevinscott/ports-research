"""Port of ``src/utils/is-point-in-range.ts``."""

from __future__ import annotations

from typing import Sequence


def is_point_in_range(point: int, bounds: Sequence[int]) -> bool:
    start, end = bounds
    return start <= point <= end
