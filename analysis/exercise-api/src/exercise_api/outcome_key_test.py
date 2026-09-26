from exercise_api.outcome_key import outcome_key


def describe_outcome_key():
    def it_is_equal_for_the_same_rules_in_a_different_order():
        a = {"ok": True, "error_type": None, "error_pos": None, "rules": [{"type": "char", "value": [97]}, {"type": "end"}], "elapsed_ns": 1}
        b = {"ok": True, "error_type": None, "error_pos": None, "rules": [{"type": "end"}, {"type": "char", "value": [97]}], "elapsed_ns": 2}
        assert outcome_key(a) == outcome_key(b)

    def it_ignores_elapsed_time():
        a = {"ok": False, "error_type": "InputParseError", "error_pos": 1, "rules": None, "elapsed_ns": 5}
        b = {**a, "elapsed_ns": 500}
        assert outcome_key(a) == outcome_key(b)

    def it_differs_on_error_position():
        a = {"ok": False, "error_type": "InputParseError", "error_pos": 1, "rules": None, "elapsed_ns": 5}
        b = {**a, "error_pos": 2}
        assert outcome_key(a) != outcome_key(b)

    def it_differs_on_rule_value():
        a = {"ok": True, "error_type": None, "error_pos": None, "rules": [{"type": "char", "value": [97]}], "elapsed_ns": 1}
        b = {"ok": True, "error_type": None, "error_pos": None, "rules": [{"type": "char", "value": [[97, 122]]}], "elapsed_ns": 1}
        assert outcome_key(a) != outcome_key(b)

    def it_differs_on_error_type():
        a = {"ok": False, "error_type": "InputParseError", "error_pos": 0, "rules": None, "elapsed_ns": 5}
        b = {**a, "error_type": "GrammarParseError"}
        assert outcome_key(a) != outcome_key(b)
