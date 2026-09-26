from __future__ import annotations

from typing import Sequence


def is_point_in_range(point: int, span: Sequence[int]) -> bool:
    start, end = span[0], span[1]
    return start <= point <= end
