import random

from measure_behavior.pools import CHARS, RANGES


def generate_atom(rng: random.Random, refs: list[str]) -> tuple:
    draw = rng.random()
    if refs and draw < 0.3:
        return ("ref", rng.choice(refs))
    if draw < 0.65:
        return ("lit", "".join(rng.choice(CHARS) for _ in range(rng.randint(1, 4))))
    items = tuple(rng.choice(RANGES) if rng.random() < 0.4 else rng.choice(CHARS) for _ in range(rng.randint(1, 3)))
    return ("cls", rng.random() < 0.25, items)
