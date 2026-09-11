FLOOR = 4


def corpus_sizes(*, max_size: int, steps: int) -> list[int]:
    """`steps` rule counts geometrically spaced between 4 and `max_size`.

    Geometric, not linear: a log-log slope fit needs points spread evenly in
    log-space, or the small sizes (where per-call overhead dominates and the
    curve is noisiest) get crowded together while the large end is sparse.
    """
    if steps < 1:
        raise ValueError("steps must be at least 1")
    if max_size < FLOOR:
        raise ValueError(f"max_size must be at least {FLOOR}")
    if steps == 1:
        return [max_size]

    ratio = (max_size / FLOOR) ** (1 / (steps - 1))
    sizes = []
    previous = 0
    for i in range(steps):
        size = max(round(FLOOR * ratio**i), previous + 1)
        sizes.append(size)
        previous = size
    return sizes
