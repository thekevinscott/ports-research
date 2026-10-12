import pytest

from measure_behavior.render_char import render_char


class Always:
    def random(self):
        return 0.0


class Never:
    def random(self):
        return 0.99


def describe_render_char():
    @pytest.mark.parametrize(("char", "expected"), [('"', '\\"'), ("\\", "\\\\"), ("\n", "\\n"), ("\t", "\\t"), ("\r", "\\r")])
    def it_always_escapes_what_a_literal_cannot_hold_raw(char, expected):
        assert render_char(char, Never(), in_class=False) == expected

    @pytest.mark.parametrize(("char", "expected"), [("]", "\\]"), ("[", "\\["), ("\\", "\\\\"), ("^", "\\x5E"), ("-", "\\x2D")])
    def it_always_escapes_what_a_class_cannot_hold_raw(char, expected):
        assert render_char(char, Never(), in_class=True) == expected

    def it_leaves_a_plain_char_raw_when_the_draw_says_so():
        assert render_char("a", Never(), in_class=False) == "a"
        assert render_char("中", Never(), in_class=True) == "中"

    @pytest.mark.parametrize(("char", "expected"), [("a", "\\x61"), ("λ", "\\u03BB"), ("😀", "\\U0001F600")])
    def it_escapes_by_code_point_width_when_the_draw_says_so(char, expected):
        assert render_char(char, Always(), in_class=False) == expected
