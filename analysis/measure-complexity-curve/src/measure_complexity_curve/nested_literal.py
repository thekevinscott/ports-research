import random

REPETITION_OPERATORS = ("?", "*", "+")


def nested_literal(rng: random.Random, depth: int) -> str:
    """A quoted 4-letter terminal wrapped in `depth` parenthesized repetition groups.

    The wrapping is the axis a quadratic graph-construction bug shows up on: more
    nesting means more group nodes the parser has to walk per rule, independent of
    how many rules or alternatives there are.
    """
    token = '"' + "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4)) + '"'
    for _ in range(depth):
        token = f"({token}){rng.choice(REPETITION_OPERATORS)}"
    return token
