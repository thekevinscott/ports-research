import math


def add(a: float, b: float) -> float:
    """Return the sum of two finite numbers."""
    for value in (a, b):
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise TypeError("add expects two finite numbers")
    return a + b
