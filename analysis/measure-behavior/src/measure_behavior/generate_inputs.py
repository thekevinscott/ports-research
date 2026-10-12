import random

from measure_behavior.mutate_string import mutate_string
from measure_behavior.sample_string import sample_string


def generate_inputs(rules: dict[str, tuple], rng: random.Random, count: int) -> list[str]:
    drawn = [sample_string(rules["root"], rules, rng) for _ in range(count // 2)]
    mutated = [mutate_string(rng.choice(drawn), rng) for _ in range(count - len(drawn) - 1)]
    return list(dict.fromkeys(["", *drawn, *mutated]))
