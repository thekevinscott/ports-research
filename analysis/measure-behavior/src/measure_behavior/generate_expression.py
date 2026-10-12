import random

from measure_behavior.generate_atom import generate_atom
from measure_behavior.is_nullable import is_nullable


def generate_expression(rng: random.Random, refs: list[str], rules: dict[str, tuple], depth: int) -> tuple:
    draw = rng.random() if depth > 0 else 1.0
    if draw < 0.3:
        return ("seq", tuple(generate_expression(rng, refs, rules, depth - 1) for _ in range(rng.randint(2, 3))))
    if draw < 0.5:
        return ("alt", tuple(generate_expression(rng, refs, rules, depth - 1) for _ in range(rng.randint(2, 3))))
    if draw < 0.7:
        # A repeated nullable expression has no fixed meaning to sample from; keep the inner part non-empty.
        inner = generate_expression(rng, refs, rules, depth - 1)
        while is_nullable(inner, rules):
            inner = generate_atom(rng, [])
        return ("rep", rng.choice("*+?"), inner)
    return generate_atom(rng, refs)
