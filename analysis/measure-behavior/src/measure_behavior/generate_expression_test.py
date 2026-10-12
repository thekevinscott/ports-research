import random

from measure_behavior.generate_expression import generate_expression
from measure_behavior.is_nullable import is_nullable


def walk(node):
    yield node
    if node[0] in ("seq", "alt"):
        for child in node[1]:
            yield from walk(child)
    if node[0] == "rep":
        yield from walk(node[2])


def describe_generate_expression():
    def it_uses_every_kind_of_node_across_seeds():
        kinds = {n[0] for seed in range(100) for n in walk(generate_expression(random.Random(seed), ["item"], {"item": ("lit", "a")}, 3))}
        assert kinds == {"lit", "cls", "ref", "seq", "alt", "rep"}

    def it_never_repeats_a_nullable_expression():
        rules = {"item": ("rep", "?", ("lit", "a"))}
        for seed in range(200):
            for node in walk(generate_expression(random.Random(seed), ["item"], rules, 3)):
                if node[0] == "rep":
                    assert not is_nullable(node[2], rules)

    def it_references_only_the_names_offered():
        for seed in range(100):
            refs = {n[1] for n in walk(generate_expression(random.Random(seed), ["item"], {"item": ("lit", "a")}, 3)) if n[0] == "ref"}
            assert refs <= {"item"}
