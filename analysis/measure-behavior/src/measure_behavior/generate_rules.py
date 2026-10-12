import random

from measure_behavior.generate_atom import generate_atom
from measure_behavior.generate_expression import generate_expression
from measure_behavior.pools import RULE_NAMES

DEPTH = 3


def generate_rules(rng: random.Random) -> dict[str, tuple]:
    helpers = rng.sample(RULE_NAMES, rng.randint(0, 3))
    rules: dict[str, tuple] = {}
    nest = []
    if rng.random() < 0.3:
        opening, closing, base = generate_atom(rng, []), generate_atom(rng, []), generate_atom(rng, [])
        rules["nest"] = ("alt", (("seq", (opening, ("ref", "nest"), closing)), base))
        nest = ["nest"]
    # Each helper references only helpers defined after it, so recursion runs through nest alone.
    for index in reversed(range(len(helpers))):
        rules[helpers[index]] = generate_expression(rng, [*helpers[index + 1 :], *nest], rules, DEPTH)
    root = generate_expression(rng, [*helpers, *nest], rules, DEPTH)
    return {"root": root, **{name: rules[name] for name in [*helpers, *nest]}}
