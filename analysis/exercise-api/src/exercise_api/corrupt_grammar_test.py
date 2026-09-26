from hypothesis import given, settings

from exercise_api.corrupt_grammar import corrupt_grammar

GRAMMAR = 'root ::= (r1 | "z")* [a-z]\nr1 ::= "q"+'


def describe_corrupt_grammar():
    @settings(max_examples=100)
    @given(corrupt_grammar(GRAMMAR))
    def it_always_changes_the_text(text):
        assert text != GRAMMAR

    @settings(max_examples=100)
    @given(corrupt_grammar('root ::= "a"'))
    def it_can_corrupt_a_grammar_without_parens_or_classes(text):
        assert text != 'root ::= "a"'
