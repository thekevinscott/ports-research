import random

# ASCII, the escapes gbnf parses, the BMP and one astral code point.
CHARS = [*"abcxyz019 -_.,:;{}[]()\"\\", "\t", "\n", "é", "λ", "中", "😀"]
MAX_LENGTH = 8


def random_string(rng: random.Random) -> str:
    return "".join(rng.choice(CHARS) for _ in range(rng.randint(1, MAX_LENGTH)))
