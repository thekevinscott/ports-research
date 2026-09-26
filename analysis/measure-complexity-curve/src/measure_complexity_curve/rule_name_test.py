from measure_complexity_curve.rule_name import rule_name


def describe_rule_name():
    def it_names_the_first_few_rules_with_single_letters():
        assert rule_name(0) == "a"
        assert rule_name(1) == "b"
        assert rule_name(25) == "z"

    def it_names_the_rule_after_z_with_two_letters():
        assert rule_name(26) == "aa"
        assert rule_name(27) == "ab"

    def it_contains_no_digits():
        for index in (0, 25, 26, 700, 12345):
            assert rule_name(index).isalpha()

    def it_is_unique_per_index():
        names = {rule_name(i) for i in range(1000)}
        assert len(names) == 1000
