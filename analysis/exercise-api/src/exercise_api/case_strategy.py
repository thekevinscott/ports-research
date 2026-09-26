from hypothesis import strategies as st

from .corrupt_grammar import corrupt_grammar
from .grammar_strategy import grammar_strategy
from .render_grammar import render_grammar
from .valid_string import valid_string

INPUT_ALPHABET = "abcxyz0189ABC .,:\"()[]{}+-"
KINDS = ["valid", "valid", "prefix", "prefix", "overrun", "random", "invalid_grammar"]
MAX_INPUT = 40


@st.composite
def case_strategy(draw) -> dict:
    rules = draw(grammar_strategy())
    grammar = render_grammar(rules)
    kind = draw(st.sampled_from(KINDS))
    if kind == "invalid_grammar":
        return {"grammar": draw(corrupt_grammar(grammar)), "input": draw(st.text(INPUT_ALPHABET, max_size=4))}
    text = draw(valid_string(rules))[:MAX_INPUT]
    if kind == "prefix":
        text = text[: draw(st.integers(0, len(text)))]
    elif kind == "overrun":
        text = (text + draw(st.text(INPUT_ALPHABET, min_size=1, max_size=2)))[:MAX_INPUT]
    elif kind == "random":
        text = draw(st.text(INPUT_ALPHABET, max_size=6))
    return {"grammar": grammar, "input": text}
