import random

from measure_behavior.render_expression import render_expression

A = ("lit", "a")
B = ("lit", "b")


def render(node):
    return render_expression(node, random.Random(0), multiline=False)


def describe_render_expression():
    def it_renders_a_literal_a_reference_and_a_class():
        assert render(A) == '"a"'
        assert render(("ref", "item")) == "item"
        assert render(("cls", False, ("x", ("0", "9")))) == "[x0-9]"
        assert render(("cls", True, ("x",))) == "[^x]"

    def it_joins_a_sequence_with_spaces_and_an_alternation_with_bars():
        assert render(("seq", (A, B))) == '"a" "b"'
        assert render(("alt", (A, B))) == '"a" | "b"'

    def it_parenthesizes_an_alternation_inside_a_sequence():
        assert render(("seq", (A, ("alt", (A, B))))) == '"a" ("a" | "b")'

    def it_puts_an_operator_straight_after_an_atom_and_after_parentheses_otherwise():
        assert render(("rep", "*", A)) == '"a"*'
        assert render(("rep", "+", ("seq", (A, B)))) == '("a" "b")+'
        assert render(("rep", "?", ("alt", (A, B)))) == '("a" | "b")?'

    def it_breaks_lines_only_after_a_bar_or_an_opening_parenthesis_when_multiline():
        x, y = ("ref", "x"), ("ref", "y")
        node = ("alt", (("seq", (x, ("alt", (x, y)))), y))
        texts = [render_expression(node, random.Random(seed), multiline=True) for seed in range(20)]
        assert any("\n" in text for text in texts)
        for text in texts:
            assert "".join(text.split()) == "".join(render(node).split())
            for line in text.split("\n")[:-1]:
                assert line.rstrip().endswith(("|", "("))
