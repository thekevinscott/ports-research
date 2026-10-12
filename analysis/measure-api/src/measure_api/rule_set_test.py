from measure_api.rule_set import rule_set


def describe_rule_set():
    def it_ignores_order_and_duplicates():
        a = [{"type": "char", "value": [97]}, {"type": "end", "value": None}]
        b = [{"type": "end", "value": None}, {"type": "char", "value": [97]}, {"type": "end", "value": None}]
        assert rule_set(a) == rule_set(b)

    def it_ignores_key_order_within_a_rule():
        assert rule_set([{"type": "char", "value": [97]}]) == rule_set([{"value": [97], "type": "char"}])

    def it_keeps_the_order_inside_a_value():
        assert rule_set([{"type": "char", "value": [97, [98, 99]]}]) != rule_set([{"type": "char", "value": [[98, 99], 97]}])

    def it_tells_types_apart():
        assert rule_set([{"type": "char", "value": [97]}]) != rule_set([{"type": "char_exclude", "value": [97]}])
