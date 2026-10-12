from measure_ast.label import label


def describe_label():
    def it_joins_name_and_arity():
        assert label("parse", 2) == "parse/2"

    def it_is_the_bare_name_when_the_arity_is_unknown():
        assert label("Rule", None) == "Rule"
