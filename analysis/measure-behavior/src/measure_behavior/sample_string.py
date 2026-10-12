import random

from measure_behavior.pools import CHARS

MAX_REPEAT = 3
DEEP = 6


def sample_string(node: tuple, rules: dict[str, tuple], rng: random.Random, depth: int = 0) -> str:
    kind = node[0]
    if kind == "lit":
        return node[1]
    if kind == "cls":
        members = [(item, item) if isinstance(item, str) else item for item in node[2]]
        if node[1]:
            return rng.choice([c for c in CHARS if not any(lo <= c <= hi for lo, hi in members)])
        lo, hi = rng.choice(members)
        return chr(rng.randint(ord(lo), ord(hi)))
    if kind == "ref":
        return sample_string(rules[node[1]], rules, rng, depth + 1)
    if kind == "seq":
        return "".join(sample_string(child, rules, rng, depth) for child in node[1])
    if kind == "alt":
        child = node[1][-1] if depth > DEEP else rng.choice(node[1])
        return sample_string(child, rules, rng, depth)
    low, high = {"*": (0, MAX_REPEAT), "+": (1, MAX_REPEAT), "?": (0, 1)}[node[1]]
    return "".join(sample_string(node[2], rules, rng, depth) for _ in range(rng.randint(low, high)))
