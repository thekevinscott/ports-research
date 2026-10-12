import random

from measure_behavior.render_grammar import render_grammar

RULES = {"root": ("seq", (("lit", "a"), ("ref", "item"))), "item": ("lit", "b")}


def describe_render_grammar():
    def it_defines_every_rule_once():
        text = render_grammar(RULES, random.Random(0)).replace("\r\n", "\n")
        definitions = [line.split("::=")[0].strip() for line in text.split("\n") if "::=" in line]
        assert sorted(definitions) == ["item", "root"]

    def it_ends_with_a_newline():
        assert render_grammar(RULES, random.Random(0)).endswith("\n")

    def it_is_deterministic_for_a_seed():
        assert render_grammar(RULES, random.Random(4)) == render_grammar(RULES, random.Random(4))

    def it_varies_layout_across_seeds():
        texts = {render_grammar(RULES, random.Random(seed)) for seed in range(40)}
        assert any("#" in text for text in texts)
        assert any("\r\n" in text for text in texts)
        assert any(not text.startswith("root") for text in texts)
