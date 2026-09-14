from exercise_api.render_grammar import render_grammar


def describe_render_grammar():
    def it_renders_a_literal_rule():
        assert render_grammar([("root", [[("literal", "foo")]])]) == 'root ::= "foo"'

    def it_joins_alternatives_with_a_bar_and_sequence_items_with_a_space():
        rules = [("root", [[("literal", "a"), ("literal", "b")], [("literal", "c")]])]
        assert render_grammar(rules) == 'root ::= "a" "b" | "c"'

    def it_renders_char_classes_with_ranges_and_negation():
        rules = [("root", [[("class", False, [("a", "z"), "0"])]]), ("r1", [[("class", True, ["x"])]])]
        assert render_grammar(rules) == "root ::= [a-z0]\nr1 ::= [^x]"

    def it_renders_references_groups_and_repetition():
        rules = [
            ("root", [[("repeat", ("group", [[("ref", "r1")], [("literal", "z")]]), "*"), ("repeat", ("ref", "r1"), "?")]]),
            ("r1", [[("repeat", ("literal", "q"), "+")]]),
        ]
        assert render_grammar(rules) == 'root ::= (r1 | "z")* r1?\nr1 ::= "q"+'
