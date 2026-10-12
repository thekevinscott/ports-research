from collections.abc import Sequence
from itertools import pairwise


def wasserstein(a: Sequence[float], b: Sequence[float]) -> float:
    """Wasserstein-1 between two empirical distributions: the area between their CDFs."""
    a, b = sorted(a), sorted(b)
    i = j = 0
    area = 0.0
    for left, right in pairwise(sorted({*a, *b})):
        while i < len(a) and a[i] <= left:
            i += 1
        while j < len(b) and b[j] <= left:
            j += 1
        area += abs(i / len(a) - j / len(b)) * (right - left)
    return area
