"""Medians compared between two groups of runs, and rank correlation, in plain numpy."""

import math

import numpy as np

SHUFFLES = 10_000
RESAMPLES = 10_000
ALPHA = 0.05


def _values(values) -> np.ndarray:
    array = np.array([math.nan if value is None else value for value in values], dtype=float)
    return array[~np.isnan(array)]


def null_gaps(on, off, *, shuffles: int = SHUFFLES, seed: int = 0) -> np.ndarray:
    """Median gaps between the two groups after each shuffle of the on/off labels."""
    on, off = _values(on), _values(off)
    pooled = np.concatenate([on, off])
    shuffled = np.random.default_rng(seed).permuted(np.tile(pooled, (shuffles, 1)), axis=1)
    return np.median(shuffled[:, : len(on)], axis=1) - np.median(shuffled[:, len(on) :], axis=1)


def permutation_p(gap: float, nulls: np.ndarray) -> float:
    """Two-sided: the share of shuffles with a gap at least this far from zero."""
    return float((np.sum(np.abs(nulls) >= abs(gap)) + 1) / (len(nulls) + 1))


def minimum_detectable_gap(nulls: np.ndarray, alpha: float = ALPHA) -> float:
    """A gap larger than this gets p < alpha against the same shuffles."""
    # p < alpha needs fewer than alpha * (shuffles + 1) - 1 shuffles at or beyond the gap.
    allowed = math.ceil(alpha * (len(nulls) + 1) - 1) - 1
    if allowed < 0:
        return math.inf
    return float(np.sort(np.abs(nulls))[::-1][allowed])


def bootstrap_interval(
    on, off, *, resamples: int = RESAMPLES, seed: int = 0, level: float = 0.95
) -> tuple[float, float]:
    """Percentile interval on the median gap, each group resampled on its own."""
    on, off = _values(on), _values(off)
    rng = np.random.default_rng(seed)
    gaps = np.median(rng.choice(on, (resamples, len(on))), axis=1) - np.median(
        rng.choice(off, (resamples, len(off))), axis=1
    )
    tail = (1 - level) / 2 * 100
    low, high = np.percentile(gaps, [tail, 100 - tail])
    return float(low), float(high)


def compare(
    on, off, *, shuffles: int = SHUFFLES, resamples: int = RESAMPLES, seed: int = 0
) -> dict:
    """The median of each group, their gap (on minus off), its p, interval and detectable size."""
    on, off = _values(on), _values(off)
    if len(on) == 0 or len(off) == 0:
        # One side has no runs: there is nothing to compare it with.
        median_on, median_off = (float(np.median(group)) if len(group) else None for group in (on, off))
        return {
            "n_on": len(on),
            "n_off": len(off),
            "median_on": median_on,
            "median_off": median_off,
            **dict.fromkeys(("gap", "low", "high", "p", "minimum_detectable_gap")),
        }
    gap = float(np.median(on) - np.median(off))
    nulls = null_gaps(on, off, shuffles=shuffles, seed=seed)
    low, high = bootstrap_interval(on, off, resamples=resamples, seed=seed)
    return {
        "n_on": len(on),
        "n_off": len(off),
        "median_on": float(np.median(on)),
        "median_off": float(np.median(off)),
        "gap": gap,
        "low": low,
        "high": high,
        "p": permutation_p(gap, nulls),
        "minimum_detectable_gap": minimum_detectable_gap(nulls),
    }


def ranks(values) -> np.ndarray:
    """1-based ranks in input order; tied values share their average rank."""
    _, inverse, counts = np.unique(np.asarray(values, dtype=float), return_inverse=True, return_counts=True)
    ends = np.cumsum(counts)
    return ((ends - counts + 1 + ends) / 2)[inverse]


def spearman(x, y) -> float:
    """Pearson correlation of the ranks, over the pairs where both values are present."""
    x = np.array([math.nan if value is None else value for value in x], dtype=float)
    y = np.array([math.nan if value is None else value for value in y], dtype=float)
    present = ~(np.isnan(x) | np.isnan(y))
    x, y = x[present], y[present]
    if len(x) < 2 or np.all(x == x[0]) or np.all(y == y[0]):
        return math.nan
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])
