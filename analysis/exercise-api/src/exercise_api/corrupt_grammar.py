from hypothesis import strategies as st

MUTATIONS = [
    lambda text: text.replace("::=", "=", 1),
    lambda text: text.replace("\n", " | zz\n", 1) if "\n" in text else text + " | zz",
    lambda text: text.replace(")", "", 1) if ")" in text else text + "\nomega ::= (",
    lambda text: text.replace("]", "", 1) if "]" in text else text + "\nomega ::= [",
    lambda text: text.replace('"', "", 1) if '"' in text else text + '\nomega ::= "',
    lambda text: text.replace("root", "main", 1),
    lambda text: "",
]


@st.composite
def corrupt_grammar(draw, text: str) -> str:
    return draw(st.sampled_from(MUTATIONS))(text)
