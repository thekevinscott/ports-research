import random
import re

# Each mirrors a failure the reference's grammar validation names, or a parse it leaves unguarded.
APPENDED = [
    'extra ::= undefined-name',
    'extra ::= ("a"',
    'extra ::= *"a"',
    'extra ::= "\\q"',
    'extra ::= "a" ::= "b"',
    '9extra ::= "a"',
    'extra ::= [a-z',
    'extra ::= "abc',
]


def corrupt_grammar(text: str, rng: random.Random) -> str:
    kind = rng.randrange(len(APPENDED) + 4)
    if kind < len(APPENDED):
        return text + APPENDED[kind]
    if kind == len(APPENDED):
        return re.sub(r"(?m)^([A-Za-z_-]+) ::=", r"\1 =", text, count=1)
    if kind == len(APPENDED) + 1:
        return re.sub(r"(?m)^([A-Za-z_-]+) ::=", r"\1 :=", text, count=1)
    if kind == len(APPENDED) + 2:
        return re.sub(r"(?m)^root ::=", "start ::=", text)
    return rng.choice(["", "# only a comment\n", "\n\n"])
