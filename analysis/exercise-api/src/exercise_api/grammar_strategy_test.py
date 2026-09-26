from hypothesis import given, settings

from exercise_api.grammar_strategy import grammar_strategy


def _items(alternatives):
    for sequence in alternatives:
        for item in sequence:
            yield item
            if item[0] == "repeat":
                yield item[1]
            if item[0] == "group":
                yield from _items(item[1])
            if item[0] == "repeat" and item[1][0] == "group":
                yield from _items(item[1][1])


def describe_grammar_strategy():
    @settings(max_examples=200)
    @given(grammar_strategy())
    def it_starts_at_root(rules):
        assert rules[0][0] == "root"

    @settings(max_examples=200)
    @given(grammar_strategy())
    def it_only_references_rules_defined_later_so_grammars_stay_finite(rules):
        names = [name for name, _ in rules]
        for index, (_, alternatives) in enumerate(rules):
            for item in _items(alternatives):
                if item[0] == "ref":
                    assert names.index(item[1]) > index

    @settings(max_examples=200)
    @given(grammar_strategy())
    def it_never_stacks_repetition_inside_a_repeated_group(rules):
        for _, alternatives in rules:
            for item in _items(alternatives):
                if item[0] == "repeat" and item[1][0] == "group":
                    assert all(inner[0] != "repeat" for inner in _items(item[1][1]))

    @settings(max_examples=200)
    @given(grammar_strategy())
    def it_never_emits_an_empty_sequence_or_class(rules):
        for _, alternatives in rules:
            assert alternatives
            for sequence in alternatives:
                assert sequence
            for item in _items(alternatives):
                if item[0] == "class":
                    assert item[2]
