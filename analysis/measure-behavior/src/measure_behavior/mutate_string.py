import random

from measure_behavior.pools import CHARS


def mutate_string(text: str, rng: random.Random) -> str:
    if not text:
        return rng.choice(CHARS)
    position = rng.randrange(len(text))
    kind = rng.choice(["truncate", "append", "delete", "insert", "replace"])
    if kind == "truncate" and len(text) > 1:
        return text[: rng.randrange(1, len(text))]
    if kind == "delete":
        return text[:position] + text[position + 1 :]
    if kind == "insert":
        return text[:position] + rng.choice(CHARS) + text[position:]
    if kind == "replace":
        return text[:position] + rng.choice([c for c in CHARS if c != text[position]]) + text[position + 1 :]
    return text + rng.choice(CHARS)
