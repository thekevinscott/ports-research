from measure_api.same_step import same_step


def rules(*values, step="whole"):
    return {"step": step, "rules": [{"type": "char", "value": [v]} for v in values]}


def error(name, pos, step="whole"):
    return {"step": step, "error": {"class": name, "pos": pos}}


def describe_same_step():
    def it_compares_rules_as_a_set():
        assert same_step(rules(97, 98), rules(98, 97))
        assert not same_step(rules(97), rules(98))

    def it_needs_the_same_step_label():
        assert not same_step(rules(97, step="prefix 1"), rules(97, step="prefix 2"))

    def it_needs_the_same_error_class_and_position():
        assert same_step(error("InputParseError", 3), error("InputParseError", 3))
        assert not same_step(error("InputParseError", 3), error("InputParseError", 4))
        assert not same_step(error("InputParseError", 3), error("ValueError", 3))

    def it_ignores_the_port_position_when_the_reference_exposes_none():
        assert same_step(error("ValueError", None), error("ValueError", 7))

    def it_never_equates_rules_with_an_error():
        assert not same_step(rules(97), error("InputParseError", 0))

    def it_never_equates_a_missing_step():
        assert not same_step(rules(97), None)
        assert not same_step(None, rules(97))
