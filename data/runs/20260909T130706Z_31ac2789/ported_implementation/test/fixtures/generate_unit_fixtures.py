"""Generate unit-level fixtures from the Python reference implementation.

Run from the repository root:

    python3 ported_implementation/test/fixtures/generate_unit_fixtures.py

The fixtures are consumed by `test/reference_units.test.ts`.
"""

import json
import sys
from pathlib import Path

REFERENCE = Path(__file__).resolve().parents[3] / "reference_implementation"
sys.path.insert(0, str(REFERENCE))

from gbnf.grammar_graph.colorize import Color, colorize  # noqa: E402
from gbnf.grammar_graph.get_input_as_code_points import get_input_as_code_points  # noqa: E402
from gbnf.grammar_graph.get_parent_stack_id import get_parent_stack_id  # noqa: E402
from gbnf.grammar_graph.get_serialized_rule_key import get_serialized_rule_key  # noqa: E402
from gbnf.grammar_graph.grammar_graph_types import (  # noqa: E402
    RuleChar,
    RuleCharExclude,
    RuleEnd,
)
from gbnf.grammar_graph.graph_node import GraphNode  # noqa: E402
from gbnf.grammar_graph.graph_pointer import GraphPointer  # noqa: E402
from gbnf.grammar_graph.print import print_graph_node, print_graph_pointer  # noqa: E402
from gbnf.grammar_graph.rule_ref import RuleRef  # noqa: E402
from gbnf.rules_builder.is_word_char import is_word_char  # noqa: E402
from gbnf.rules_builder.parse_char import parse_char  # noqa: E402
from gbnf.rules_builder.parse_name import parse_name  # noqa: E402
from gbnf.rules_builder.parse_space import parse_space  # noqa: E402
from gbnf.utils.errors.build_error_position import build_error_position  # noqa: E402
from gbnf.utils.errors.get_input_as_string import get_input_as_string  # noqa: E402
from gbnf.utils.is_point_in_range import is_point_in_range  # noqa: E402


def attempt(fn, *args):
    try:
        return {"args": list(args), "result": fn(*args)}
    except Exception as err:  # noqa: BLE001
        return {"args": list(args), "error": type(err).__name__, "message": str(err)}


def identity_colorize(text, _color):
    return str(text)


def mock_pointer(*ids):
    """Build a pointer whose parent chain is `ids`, outermost last."""
    pointer = None
    for stack_id, path_id, step_id in ids:
        node = GraphNode(
            RuleEnd(),
            {"stackId": stack_id, "pathId": path_id, "stepId": step_id},
        )
        pointer = GraphPointer(node, pointer)
    return pointer


def parent_stack_id_cases():
    cases = []
    for ids in [
        [(0, 0, 0)],
        [(0, 0, 0), (1, 1, 1)],
        [(0, 0, 0), (1, 1, 1), (2, 2, 2)],
    ]:
        pointer = mock_pointer(*ids)
        cases.append(
            {
                "ids": ids,
                "plain": get_parent_stack_id(pointer, identity_colorize),
                "colorized": get_parent_stack_id(pointer, colorize),
            },
        )
    return cases


def print_node_cases():
    cases = []

    def node_case(name, node, show_position):
        cases.append(
            {
                "name": name,
                "showPosition": show_position,
                "plain": print_graph_node(node)(
                    {"colorize": identity_colorize, "show_position": show_position},
                ),
                "colorized": print_graph_node(node)(
                    {"colorize": colorize, "show_position": show_position},
                ),
            },
        )

    meta = {"stackId": 0, "pathId": 1, "stepId": 2}
    node_case("char", GraphNode(RuleChar(value=[65]), meta), False)
    node_case("char-with-position", GraphNode(RuleChar(value=[65]), meta), True)
    node_case("char-range", GraphNode(RuleChar(value=[[97, 122]]), meta), False)
    node_case("char-newline", GraphNode(RuleChar(value=[10]), meta), False)
    node_case("char-mixed", GraphNode(RuleChar(value=[[97, 99], 122, 10]), meta), True)
    node_case("ref", GraphNode(RuleRef(200), meta), True)
    node_case(
        "chained",
        GraphNode(RuleChar(value=[65]), meta, GraphNode(RuleChar(value=[66]), meta)),
        True,
    )
    return cases


def print_pointer_cases():
    pointer = mock_pointer((0, 0, 0), (1, 2, 3))
    return [
        {
            "ids": [[0, 0, 0], [1, 2, 3]],
            "plain": print_graph_pointer(pointer)({"colorize": identity_colorize}),
            "colorized": print_graph_pointer(pointer)({"colorize": colorize}),
        },
    ]


def main() -> None:
    fixtures = {
        "colors": {
            "BLUE": Color.BLUE,
            "CYAN": Color.CYAN,
            "GREEN": Color.GREEN,
            "RED": Color.RED,
            "GRAY": Color.GRAY,
            "YELLOW": Color.YELLOW,
        },
        "colorize": [
            {"args": ["hello", Color.BLUE], "result": colorize("hello", Color.BLUE)},
            {"args": [123, Color.RED], "result": colorize(123, Color.RED)},
        ],
        "isWordChar": [
            attempt(is_word_char, c)
            for c in ["a", "z", "A", "Z", "0", "9", "-", "_", " ", "\n", "[", "ぁ"]
        ],
        "parseSpace": [
            attempt(parse_space, *args)
            for args in [
                ("   abc", 0, False),
                ("   abc", 0, True),
                ("\n\n abc", 0, False),
                ("\n\n abc", 0, True),
                ("# comment\nabc", 0, False),
                ("# comment\nabc", 0, True),
                ("abc", 0, True),
                ("  \t \r\n x", 0, True),
                ("  \t \r\n x", 0, False),
                ("", 0, True),
                ("a", 5, True),
            ]
        ],
        "parseName": [
            attempt(parse_name, *args)
            for args in [
                ("root ::= x", 0),
                ("foo-bar ::= x", 0),
                ("foo_bar ::= x", 0),
                ("  root", 2),
                ("123", 0),
                ("", 0),
                ("root", 4),
            ]
        ],
        "parseChar": [
            attempt(parse_char, *args)
            for args in [
                ("a", 0),
                ("abc", 1),
                ("\\x41", 0),
                ("\\u0041", 0),
                ("\\U0001F4A9", 0),
                ("\\t", 0),
                ("\\r", 0),
                ("\\n", 0),
                ('\\"', 0),
                ("\\[", 0),
                ("\\]", 0),
                ("\\\\", 0),
                ("\\q", 0),
                ("a", 1),
                ("", 0),
            ]
        ],
        "buildErrorPosition": [
            attempt(build_error_position, *args)
            for args in [
                ("", 0),
                ("abc", 0),
                ("abc", 2),
                ("abc", 5),
                ("abc\ndef", 4),
                ("abc\ndef\nghi", 9),
                ("a\nb\nc\nd\ne", 7),
                ("abc\n\ndef", 5),
            ]
        ],
        "getInputAsString": [
            attempt(get_input_as_string, src) for src in ["abc", 97, [97, 98, 99], []]
        ],
        "getInputAsCodePoints": [
            attempt(get_input_as_code_points, src)
            for src in ["abc", 99, [99, 100, 101], "", "あ", "😀"]
        ],
        "isPointInRange": [
            attempt(is_point_in_range, *args)
            for args in [(5, (0, 10)), (0, (0, 10)), (10, (0, 10)), (11, (0, 10)), (-1, (0, 10))]
        ],
        "getSerializedRuleKey": [
            {"rule": {"type": "end"}, "result": get_serialized_rule_key(RuleEnd())},
            {
                "rule": {"type": "char", "value": [97]},
                "result": get_serialized_rule_key(RuleChar(value=[97])),
            },
            {
                "rule": {"type": "char", "value": [[97, 122], 65]},
                "result": get_serialized_rule_key(RuleChar(value=[[97, 122], 65])),
            },
            {
                "rule": {"type": "char_exclude", "value": [10]},
                "result": get_serialized_rule_key(RuleCharExclude(value=[10])),
            },
            {"rule": {"type": "ref", "value": 99}, "result": get_serialized_rule_key(RuleRef(99))},
        ],
        "getParentStackId": parent_stack_id_cases(),
        "printGraphNode": print_node_cases(),
        "printGraphPointer": print_pointer_cases(),
    }

    out = Path(__file__).parent / "unit_fixtures.json"
    out.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out}")  # noqa: T201


if __name__ == "__main__":
    main()
