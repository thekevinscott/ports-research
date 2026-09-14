import string

from hypothesis import strategies as st

NEGATION_ALPHABET = string.ascii_letters + string.digits + " !#$%&'()*+,-./:;<=>?@"
REPEAT_COUNTS = {"?": (0, 1), "*": (0, 2), "+": (1, 3)}


def _class_members(members) -> set[str]:
    chars = set()
    for member in members:
        if isinstance(member, tuple):
            chars.update(chr(c) for c in range(ord(member[0]), ord(member[1]) + 1))
        else:
            chars.add(member)
    return chars


@st.composite
def valid_string(draw, rules: list[tuple]) -> str:
    by_name = dict(rules)

    def item(node) -> str:
        match node:
            case ("literal", text):
                return text
            case ("class", negate, members):
                chars = _class_members(members)
                pool = sorted(set(NEGATION_ALPHABET) - chars) if negate else sorted(chars)
                return draw(st.sampled_from(pool))
            case ("ref", name):
                return alternatives(by_name[name])
            case ("group", alts):
                return alternatives(alts)
            case ("repeat", inner, op):
                low, high = REPEAT_COUNTS[op]
                return "".join(item(inner) for _ in range(draw(st.integers(low, high))))
        raise ValueError(f"unknown item {node!r}")

    def alternatives(alts) -> str:
        return "".join(item(node) for node in draw(st.sampled_from(alts)))

    return alternatives(by_name["root"])
