from typing import NamedTuple

from measure_ast.pair_functions import normalise_name, pair_functions


class Fn(NamedTuple):
    name: str
    arity: int


def describe_normalise_name():
    def it_folds_snake_and_camel_case_together():
        assert normalise_name("parse_rule") == normalise_name("parseRule") == "parserule"

    def it_drops_leading_underscores():
        assert normalise_name("__parse_rule") == "parserule"

    def it_drops_the_typescript_private_marker():
        assert normalise_name("#parseRule") == "parserule"

    def it_folds_a_dunder_to_its_bare_name():
        assert normalise_name("__init__") == "init"

    def it_folds_screaming_case():
        assert normalise_name("PARSE_NAME") == "parsename"


def describe_pair_functions():
    def it_pairs_by_normalised_name_and_arity():
        port, reference = [Fn("parseRule", 2)], [Fn("parse_rule", 2)]
        assert pair_functions(port, reference) == ([(port[0], reference[0])], [], [])

    def it_does_not_pair_the_same_name_at_a_different_arity():
        port, reference = [Fn("parse", 1)], [Fn("parse", 2)]
        assert pair_functions(port, reference) == ([], port, reference)

    def it_leaves_unmatched_functions_on_their_own_side():
        port, reference = [Fn("a", 0), Fn("b", 0)], [Fn("b", 0), Fn("c", 0)]
        assert pair_functions(port, reference) == ([(port[1], reference[0])], [port[0]], [reference[1]])

    def it_pairs_functions_sharing_a_key_in_the_order_given():
        port = [Fn("__init__", 1), Fn("__init__", 1), Fn("__init__", 1)]
        reference = [Fn("__init__", 1), Fn("init", 1)]
        pairs, port_only, reference_only = pair_functions(port, reference)
        assert [(p is port[i], r is reference[i]) for i, (p, r) in enumerate(pairs)] == [(True, True), (True, True)]
        assert port_only == [port[2]]
        assert reference_only == []
