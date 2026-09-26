from hypothesis import strategies as st

RULE_NAMES = ["root", "alpha", "beta", "gamma"]
LITERAL_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 "
CLASS_RANGES = [("a", "z"), ("A", "Z"), ("0", "9"), ("a", "f"), ("0", "3")]
CLASS_CHARS = "abcxyz0189ABC.,:"
REPETITIONS = ["?", "*", "+"]

literal = st.builds(lambda text: ("literal", text), st.text(LITERAL_ALPHABET, min_size=1, max_size=4))
char_class = st.builds(
    lambda negate, members: ("class", negate, members),
    st.booleans(),
    st.lists(st.one_of(st.sampled_from(CLASS_RANGES), st.sampled_from(CLASS_CHARS)), min_size=1, max_size=3, unique=True),
)


@st.composite
def _item(draw, referable: list[str], depth: int, allow_repeat: bool):
    choices = [literal, char_class]
    if referable:
        choices.append(st.builds(lambda name: ("ref", name), st.sampled_from(referable)))
    repeat = allow_repeat and draw(st.booleans())
    if depth > 0 and draw(st.integers(0, 3)) == 0:
        alternatives = draw(_alternatives(referable, depth - 1, allow_repeat and not repeat))
        item = ("group", alternatives)
    else:
        item = draw(st.one_of(choices))
    if repeat:
        return ("repeat", item, draw(st.sampled_from(REPETITIONS)))
    return item


@st.composite
def _alternatives(draw, referable: list[str], depth: int, allow_repeat: bool):
    sequence = st.lists(_item(referable, depth, allow_repeat), min_size=1, max_size=3)
    return draw(st.lists(sequence, min_size=1, max_size=3))


@st.composite
def grammar_strategy(draw):
    names = RULE_NAMES[: draw(st.integers(1, len(RULE_NAMES)))]
    return [(name, draw(_alternatives(names[index + 1 :], depth=2, allow_repeat=True))) for index, name in enumerate(names)]
