from hypothesis import given, settings

from exercise_api.valid_string import valid_string


def describe_valid_string():
    @given(valid_string([("root", [[("literal", "foo"), ("literal", "bar")]])]))
    def it_concatenates_a_sequence_of_literals(text):
        assert text == "foobar"

    @settings(max_examples=50)
    @given(valid_string([("root", [[("literal", "a")], [("literal", "b")]])]))
    def it_picks_one_alternative(text):
        assert text in {"a", "b"}

    @settings(max_examples=50)
    @given(valid_string([("root", [[("class", False, [("a", "c"), "9"])]])]))
    def it_picks_a_member_of_a_char_class(text):
        assert text in {"a", "b", "c", "9"}

    @settings(max_examples=50)
    @given(valid_string([("root", [[("class", True, [("a", "z"), ("A", "Z")])]])]))
    def it_picks_a_non_member_of_a_negated_class(text):
        assert len(text) == 1
        assert not text.isalpha()

    @settings(max_examples=50)
    @given(valid_string([("root", [[("ref", "r1")]]), ("r1", [[("literal", "z")]])]))
    def it_follows_references(text):
        assert text == "z"

    @settings(max_examples=50)
    @given(valid_string([("root", [[("repeat", ("literal", "a"), "?")]])]))
    def it_repeats_optional_zero_or_one_times(text):
        assert text in {"", "a"}

    @settings(max_examples=50)
    @given(valid_string([("root", [[("repeat", ("group", [[("literal", "ab")]]), "+")]])]))
    def it_repeats_plus_at_least_once(text):
        assert text and len(text) % 2 == 0 and set(text) <= {"a", "b"}

    @settings(max_examples=50)
    @given(valid_string([("root", [[("repeat", ("literal", "a"), "*")]])]))
    def it_repeats_star_zero_or_more_times(text):
        assert set(text) <= {"a"}
