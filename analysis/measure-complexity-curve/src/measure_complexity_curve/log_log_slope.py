import math


def log_log_slope(*, sizes: list[float], seconds: list[float]) -> float:
    """Least-squares slope of log(seconds) against log(sizes).

    Scale-invariant on purpose: a language-to-language comparison can't use
    absolute times, but the exponent of the underlying power law — 1 for
    linear, 2 for quadratic — is comparable across implementations regardless
    of constant-factor differences between languages.
    """
    if len(sizes) != len(seconds):
        raise ValueError("sizes and seconds must be the same length")
    if len(sizes) < 2:
        raise ValueError("at least two points are required to fit a slope")

    xs = [math.log(size) for size in sizes]
    ys = [math.log(second) for second in seconds]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return numerator / denominator
