import pytest

from ..grammar_graph.grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from ..grammar_graph.rule_ref import RuleRef
from ..rules_builder.rules_builder_types import (
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
)
from .build_rule_stack import build_rule_stack


def ichar(value):
    return InternalRuleDefChar(value)


def ichar_alt(value):
    return InternalRuleDefCharAlt(value)


def ichar_rng_upper(value):
    return InternalRuleDefCharRngUpper(value)


def ichar_not(value):
    return InternalRuleDefCharNot(value)


def ialt():
    return InternalRuleDefAlt()


def iend():
    return InternalRuleDefEnd()


def iref(value):
    return InternalRuleDefReference(value)


def cp(char):
    return ord(char)


def make_range(lower, upper):
    return [
        lower if isinstance(lower, int) else cp(lower),
        upper if isinstance(upper, int) else cp(upper),
    ]


def test_it_builds_rule_stack_for_a_single_path():
    assert build_rule_stack([ichar([120])]) == [[RuleChar([120]), RuleEnd()]]


def test_it_builds_rule_stack_for_two_alternate_paths():
    assert build_rule_stack([ichar([cp("x")]), ialt(), ichar([cp("y")])]) == [
        [RuleChar([cp("x")]), RuleEnd()],
        [RuleChar([cp("y")]), RuleEnd()],
    ]


def test_it_builds_rule_stack_for_three_alternate_paths():
    assert build_rule_stack(
        [
            ichar([cp("x")]),
            ialt(),
            ichar([cp("y")]),
            ialt(),
            ichar([cp("z")]),
        ]
    ) == [
        [RuleChar([cp("x")]), RuleEnd()],
        [RuleChar([cp("y")]), RuleEnd()],
        [RuleChar([cp("z")]), RuleEnd()],
    ]


def test_it_builds_rule_stack_for_char_not():
    assert build_rule_stack(
        [
            ichar_not([cp("x")]),
            ialt(),
            ichar_not([cp("y")]),
            ialt(),
            ichar_not([cp("z")]),
        ]
    ) == [
        [RuleCharExclude([cp("x")]), RuleEnd()],
        [RuleCharExclude([cp("y")]), RuleEnd()],
        [RuleCharExclude([cp("z")]), RuleEnd()],
    ]


def test_it_builds_rule_stack_for_mixed_char_and_char_not():
    assert build_rule_stack(
        [
            ichar_not([cp("x")]),
            ialt(),
            ichar([cp("y")]),
            ialt(),
            ichar_not([cp("z")]),
        ]
    ) == [
        [RuleCharExclude([cp("x")]), RuleEnd()],
        [RuleChar([cp("y")]), RuleEnd()],
        [RuleCharExclude([cp("z")]), RuleEnd()],
    ]


def test_it_builds_rule_stack_for_char_not_with_two_characters_and_a_range():
    assert build_rule_stack(
        [
            ichar_not([cp("x")]),
            ichar_alt(cp("y")),
            ichar_alt(cp("z")),
            ichar_rng_upper(130),
        ]
    ) == [[RuleCharExclude([120, 121, make_range(122, 130)]), RuleEnd()]]


@pytest.mark.parametrize(
    ("grammar", "input", "expected"),
    [
        (
            "[a-z]",
            [ichar([cp("a")]), ichar_rng_upper(cp("z")), iend()],
            [[RuleChar([make_range("a", "z")]), RuleEnd()]],
        ),
        (
            "[a-zA-Z]",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                iend(),
            ],
            [[RuleChar([make_range("a", "z"), make_range("A", "Z")]), RuleEnd()]],
        ),
        (
            "[a-zA-Z0-9]",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ichar_alt(cp("0")),
                ichar_rng_upper(cp("9")),
                iend(),
            ],
            [
                [
                    RuleChar(
                        [
                            make_range("a", "z"),
                            make_range("A", "Z"),
                            make_range("0", "9"),
                        ]
                    ),
                    RuleEnd(),
                ]
            ],
        ),
    ],
)
def test_it_builds_rule_stack_for_a_char_with_no_modifiers(grammar, input, expected):
    assert build_rule_stack(input) == expected


@pytest.mark.parametrize(
    ("grammar", "input", "expected"),
    [
        (
            "[a-z]?",
            [ichar([cp("a")]), ichar_rng_upper(cp("z")), ialt(), iend()],
            [
                [RuleChar([make_range("a", "z")]), RuleEnd()],
                [RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z]?",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ialt(),
                iend(),
            ],
            [
                [RuleChar([make_range("a", "z"), make_range("A", "Z")]), RuleEnd()],
                [RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z0-9]?",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ichar_alt(cp("0")),
                ichar_rng_upper(cp("9")),
                ialt(),
                iend(),
            ],
            [
                [
                    RuleChar(
                        [
                            make_range("a", "z"),
                            make_range("A", "Z"),
                            make_range("0", "9"),
                        ]
                    ),
                    RuleEnd(),
                ],
                [RuleEnd()],
            ],
        ),
    ],
)
def test_it_builds_rule_stack_for_a_char_with_question_mark_modifier(
    grammar, input, expected
):
    assert build_rule_stack(input) == expected


@pytest.mark.parametrize(
    ("grammar", "input", "expected"),
    [
        (
            "[a-z]+",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                iref(1),
                ialt(),
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                iend(),
            ],
            [
                [RuleChar([make_range("a", "z")]), RuleRef(1), RuleEnd()],
                [RuleChar([make_range("a", "z")]), RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z]+",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                iref(1),
                ialt(),
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                iend(),
            ],
            [
                [
                    RuleChar([make_range("a", "z"), make_range("A", "Z")]),
                    RuleRef(1),
                    RuleEnd(),
                ],
                [RuleChar([make_range("a", "z"), make_range("A", "Z")]), RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z0-9]+",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ichar_alt(cp("0")),
                ichar_rng_upper(cp("9")),
                iref(1),
                ialt(),
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ichar_alt(cp("0")),
                ichar_rng_upper(cp("9")),
                iend(),
            ],
            [
                [
                    RuleChar(
                        [
                            make_range("a", "z"),
                            make_range("A", "Z"),
                            make_range("0", "9"),
                        ]
                    ),
                    RuleRef(1),
                    RuleEnd(),
                ],
                [
                    RuleChar(
                        [
                            make_range("a", "z"),
                            make_range("A", "Z"),
                            make_range("0", "9"),
                        ]
                    ),
                    RuleEnd(),
                ],
            ],
        ),
    ],
)
def test_it_builds_rule_stack_for_a_char_with_plus_modifier(grammar, input, expected):
    assert build_rule_stack(input) == expected


@pytest.mark.parametrize(
    ("grammar", "input", "expected"),
    [
        (
            "[a-z]*",
            [ichar([cp("a")]), ichar_rng_upper(cp("z")), iref(1), ialt(), iend()],
            [
                [RuleChar([make_range("a", "z")]), RuleRef(1), RuleEnd()],
                [RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z]*",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                iref(1),
                ialt(),
                iend(),
            ],
            [
                [
                    RuleChar([make_range("a", "z"), make_range("A", "Z")]),
                    RuleRef(1),
                    RuleEnd(),
                ],
                [RuleEnd()],
            ],
        ),
        (
            "[a-zA-Z0-9]*",
            [
                ichar([cp("a")]),
                ichar_rng_upper(cp("z")),
                ichar_alt(cp("A")),
                ichar_rng_upper(cp("Z")),
                ichar_alt(cp("0")),
                ichar_rng_upper(cp("9")),
                iref(1),
                ialt(),
                iend(),
            ],
            [
                [
                    RuleChar(
                        [
                            make_range("a", "z"),
                            make_range("A", "Z"),
                            make_range("0", "9"),
                        ]
                    ),
                    RuleRef(1),
                    RuleEnd(),
                ],
                [RuleEnd()],
            ],
        ),
    ],
)
def test_it_builds_rule_stack_for_a_char_with_asterisk_modifier(
    grammar, input, expected
):
    assert build_rule_stack(input) == expected


def test_char_with_range():
    input = [
        ichar([cp("a")]),
        ichar_rng_upper(cp("z")),
        ichar_alt(cp("A")),
        ichar_rng_upper(cp("Z")),
        ichar_alt(cp("_")),
        iend(),
    ]

    assert build_rule_stack(input) == [
        [
            RuleChar([make_range("a", "z"), make_range("A", "Z"), cp("_")]),
            RuleEnd(),
        ]
    ]


def test_it_builds_rule_stack_for_situation_root_ws_plus_newline_ws_star():
    input = [
        ichar([32]),
        ichar_alt(92),
        ichar_alt(110),
        iref(4),
        ialt(),
        iend(),
    ]

    assert build_rule_stack(input) == [
        [RuleChar([32, 92, 110]), RuleRef(4), RuleEnd()],
        [RuleEnd()],
    ]


def test_it_builds_rule_stack_for_situation_root_char_plus_char_range():
    input = [
        ichar([cp("a")]),
        ichar_rng_upper(cp("z")),
        ichar_alt(cp("A")),
        ichar_rng_upper(cp("Z")),
        iref(1),
        ialt(),
        ichar([cp("a")]),
        ichar_rng_upper(cp("z")),
        ichar_alt(cp("A")),
        ichar_rng_upper(cp("Z")),
        iend(),
    ]

    assert build_rule_stack(input) == [
        [
            RuleChar([make_range("a", "z"), make_range("A", "Z")]),
            RuleRef(1),
            RuleEnd(),
        ],
        [
            RuleChar([make_range("a", "z"), make_range("A", "Z")]),
            RuleEnd(),
        ],
    ]
