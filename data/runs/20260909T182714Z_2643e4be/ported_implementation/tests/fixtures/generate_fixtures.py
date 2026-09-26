"""Generate differential-test fixtures from the Python reference implementation.

Run from the repository root:

    python3 ported_implementation/tests/fixtures/generate_fixtures.py

The emitted JSON captures, for a corpus of grammars, exactly what the reference
implementation produces: the internal rules from the RulesBuilder, the stacked
rules from build_rule_stack, and the rules exposed by the parse state after each
chunk of input (plus the errors raised along the way). The TypeScript port is
asserted against the same JSON in fixtures.test.ts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "reference_implementation"))

from gbnf import GBNF  # noqa: E402
from gbnf.grammar_graph.rule_ref import RuleRef  # noqa: E402
from gbnf.grammar_parser.build_rule_stack import build_rule_stack  # noqa: E402
from gbnf.rules_builder import RulesBuilder  # noqa: E402


def serialize_error(err: BaseException) -> dict:
    return {"type": type(err).__name__, "message": str(err)}


def serialize_internal_rule(rule) -> dict:
    out = {"type": type(rule).__name__}
    if hasattr(rule, "value"):
        out["value"] = rule.value
    return out


def serialize_rule(rule) -> dict:
    # RuleRef is not a Rule subclass, so it has no `type` in its __dict__.
    if isinstance(rule, RuleRef):
        return {"type": "RuleRef", "value": rule.value}
    return rule.__dict__


def sorted_rules(rules) -> list[dict]:
    # The reference stores referenced nodes in a `set`, so pointer (and
    # therefore rule) ordering is not stable across implementations; compare
    # the rules as a sorted collection.
    return sorted(
        (serialize_rule(rule) for rule in rules),
        key=lambda rule: json.dumps(rule, sort_keys=True),
    )


def build_case(name: str, grammar: str, sequences: list[list[str]]) -> dict:
    case: dict = {"name": name, "grammar": grammar, "sequences": []}

    try:
        builder = RulesBuilder(grammar)
        case["internalRules"] = [
            [serialize_internal_rule(rule) for rule in rules]
            for rules in builder.rules
        ]
        case["symbolIds"] = dict(builder.symbol_ids.items())
    except Exception as err:  # noqa: BLE001
        case["internalRules"] = None
        case["symbolIds"] = None
        case["builderError"] = serialize_error(err)

    if case["internalRules"] is not None:
        try:
            case["stackedRules"] = [
                [
                    [serialize_rule(rule) for rule in path]
                    for path in build_rule_stack(rules)
                ]
                for rules in builder.rules
            ]
        except Exception as err:  # noqa: BLE001
            case["stackedRules"] = None
            case["stackError"] = serialize_error(err)

    for sequence in sequences:
        entry: dict = {"inputs": sequence, "steps": []}
        try:
            state = GBNF(grammar, sequence[0])
            entry["steps"].append(
                {"input": sequence[0], "rules": sorted_rules(state)},
            )
            for chunk in sequence[1:]:
                state = state.add(chunk)
                entry["steps"].append({"input": chunk, "rules": sorted_rules(state)})
        except Exception as err:  # noqa: BLE001
            entry["error"] = serialize_error(err)
        case["sequences"].append(entry)

    return case


JSON_GRAMMAR = """
root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws

object ::=
  "{" ws (
            string ":" ws value
    ("," ws string ":" ws value)*
  )? "}" ws

array  ::=
  "[" ws (
            value
    ("," ws value)*
  )? "]" ws

string ::=
  "\\"" (
    [^"\\\\] |
    "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
  )* "\\"" ws

number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws

ws ::= ([ \\t\\n] ws)?
"""

ARITHMETIC_GRAMMAR = """
root  ::= (expr "=" ws term "\\n")+
expr  ::= term ([-+*/] term)*
term  ::= ident | num | "(" ws expr ")" ws
ident ::= [a-z] [a-z0-9_]* ws
num   ::= [0-9]+ ws
ws    ::= [ \\t\\n]*
"""

CASES: list[tuple[str, str, list[list[str]]]] = [
    (
        "single literal",
        'root ::= "foo"',
        [["f", "o", "o"], ["foo"], ["fo"], [""], ["b"], ["fooo"], ["fox"]],
    ),
    (
        "char range",
        "root ::= [a-z]",
        [["a"], ["z"], ["m"], ["A"], ["0"]],
    ),
    (
        "one or more",
        "root ::= [a-z]+",
        [["a"], ["abc"], ["a", "b", "c"], [""], ["aB"]],
    ),
    (
        "zero or more",
        'root ::= "a"*',
        [[""], ["a"], ["aaaa"], ["a", "a"], ["b"]],
    ),
    (
        "optional",
        'root ::= "a"? "b"',
        [["b"], ["ab"], ["a", "b"], ["aa"], ["c"]],
    ),
    (
        "alternates",
        'root ::= "a" | "b" | "cd"',
        [["a"], ["b"], ["c", "d"], ["cd"], ["d"], ["cb"]],
    ),
    (
        "grouped alternates",
        'root ::= ("a" | "b")+ "c"',
        [["abc"], ["a", "b", "c"], ["c"], ["ac"], ["abd"]],
    ),
    (
        "rule references",
        'root ::= expr\nexpr ::= "1" "+" "2"',
        [["1+2"], ["1", "+", "2"], ["1-"]],
    ),
    (
        "recursive rule",
        'root ::= "a" root | "b"',
        [["b"], ["ab"], ["aaab"], ["a", "a", "b"], ["c"], ["aac"]],
    ),
    (
        "char alternates",
        "root ::= [abc]",
        [["a"], ["b"], ["c"], ["d"]],
    ),
    (
        "mixed ranges and alternates",
        "root ::= [a-cx-z0_]+",
        [["a"], ["c"], ["x"], ["0"], ["_"], ["abcxyz0_"], ["d"], ["w"]],
    ),
    (
        "trailing dash in class",
        "root ::= [a-]",
        [["a"], ["-"], ["b"]],
    ),
    (
        "negated char class",
        'root ::= [^a-z] "!"',
        [["A!"], ["0", "!"], ["a!"], ["A?"]],
    ),
    (
        "escapes",
        'root ::= "\\n" | "\\t" | "\\r" | "\\x41" | "\\u00e9" | "\\\\" | "\\"" | "[" | "]"',
        [["\n"], ["\t"], ["\r"], ["A"], ["é"], ["\\"], ['"'], ["["], ["]"], ["q"]],
    ),
    (
        "unicode range",
        "root ::= [\\u00e0-\\u00ff]+",
        [["é"], ["àÿ"], ["a"]],
    ),
    (
        "long unicode escape",
        'root ::= "\\U0001F600"',
        [["\U0001f600"], ["a"]],
    ),
    (
        "comments and whitespace",
        '# leading comment\nroot ::= "a" # trailing comment\n     | "b"\n',
        [["a"], ["b"], ["c"]],
    ),
    (
        "carriage returns",
        'root ::= "a"\r\nother ::= "b"\r\n',
        [["a"], ["b"]],
    ),
    (
        "nested groups",
        'root ::= ("a" ("b" | "c") "d")+',
        [["abd"], ["acd"], ["abdacd"], ["a", "b", "d"], ["aa"]],
    ),
    (
        "sequence of rules",
        'root ::= a b\na ::= "x"+\nb ::= "y"',
        [["xy"], ["xxxy"], ["x", "x", "y"], ["y"], ["xz"]],
    ),
    (
        "names with separators",
        'root ::= my-rule\nmy-rule ::= my_other-rule\nmy_other-rule ::= "z"',
        [["z"], ["a"]],
    ),
    ("json", JSON_GRAMMAR, [
        ['{"a": 1}'],
        ["{", '"', "a", '"', ":", " ", "1", "}"],
        ["[1, 2, 3]"],
        ["true"],
        ['"\\u00e9"'],
        ["-12.5e+3"],
        ["{]"],
        ["nul"],
    ]),
    ("arithmetic", ARITHMETIC_GRAMMAR, [
        ["x = 1 + 2\n"],
        ["a1_b = (3 * 4)\n"],
        ["x", " ", "=", " ", "1", "\n"],
        ["X = 1\n"],
        ["1 = 1\n"],
    ]),
    # Grammars that fail to parse
    ("empty grammar", "", [[""]]),
    ("whitespace only grammar", "   \n  ", [[""]]),
    ("missing root", 'foo ::= "a"', [[""]]),
    ("undefined rule", "root ::= missing", [[""]]),
    ("missing assignment", 'root := "a"', [[""]]),
    ("missing rule body", "root ::= ", [[""]]),
    ("quantifier without item", 'root ::= *"a"', [[""]]),
    ("unclosed group", 'root ::= ("a"', [[""]]),
    ("unterminated string", 'root ::= "a', [[""]]),
    ("unterminated char class", "root ::= [a", [[""]]),
    ("unknown escape", 'root ::= "\\q"', [[""]]),
    ("trailing garbage", 'root ::= "a" )', [[""]]),
    ("name expected", '::= "a"', [[""]]),
]


# Grammars fuzzed with seeded random input, chunked at random boundaries so that
# failures land on later calls to `add` (which exercises the accumulated
# previous-input positions in InputParseError).
FUZZED_GRAMMARS: list[tuple[str, str, str]] = [
    ("fuzz json", JSON_GRAMMAR, '{}[]",:0123456789.eE+-truefalsnl \t\n'),
    ("fuzz arithmetic", ARITHMETIC_GRAMMAR, "abz019_+-*/()= \t\n"),
    ("fuzz nested groups", 'root ::= ("a" ("b" | "c") "d")+', "abcd"),
    ("fuzz recursion", 'root ::= "a" root | "b"', "ab"),
    ("fuzz char classes", 'root ::= [^a-z0-9]+ "|" [a-cx-z]*', "abcxyz09-|!"),
    ("fuzz quantifiers", 'root ::= "a"? ("b" | "c")* "d"+ "e"', "abcde"),
]


def build_fuzz_cases(seed: int = 20240509, per_grammar: int = 40) -> list[dict]:
    import random

    rand = random.Random(seed)
    cases = []
    for name, grammar, alphabet in FUZZED_GRAMMARS:
        sequences = []
        for _ in range(per_grammar):
            text = "".join(
                rand.choice(alphabet) for _ in range(rand.randint(1, 24))
            )
            chunks = []
            pos = 0
            while pos < len(text):
                size = rand.randint(1, 4)
                chunks.append(text[pos : pos + size])
                pos += size
            sequences.append(chunks)
        cases.append(build_case(name, grammar, sequences))
    return cases


MUTATION_ALPHABET = '"[]()|*+?^-\\:=# \t\nabz09_.'


def build_grammar_fuzz_cases(seed: int = 8675309, count: int = 120) -> list[dict]:
    """Mutate valid grammars into (mostly) invalid ones to compare error paths."""
    import random

    rand = random.Random(seed)
    bases = [grammar for _, grammar, _ in CASES[:21]]
    cases = []
    for i in range(count):
        grammar = rand.choice(bases)
        for _ in range(rand.randint(1, 3)):
            if not grammar:
                break
            op = rand.choice(["delete", "insert", "replace", "truncate"])
            pos = rand.randrange(len(grammar))
            char = rand.choice(MUTATION_ALPHABET)
            if op == "delete":
                grammar = grammar[:pos] + grammar[pos + 1 :]
            elif op == "insert":
                grammar = grammar[:pos] + char + grammar[pos:]
            elif op == "replace":
                grammar = grammar[:pos] + char + grammar[pos + 1 :]
            else:
                grammar = grammar[:pos]
        cases.append(build_case(f"grammar fuzz {i}", grammar, [["a"], ["ab"]]))
    return cases


ERROR_POSITION_CASES: list[tuple[str, int]] = [
    ("", 0),
    ("abc", 0),
    ("abc", 2),
    ("abc", 3),
    ("abc", 5),
    ("abc", -1),
    ("one\ntwo\nthree\nfour", 0),
    ("one\ntwo\nthree\nfour", 4),
    ("one\ntwo\nthree\nfour", 10),
    ("one\ntwo\nthree\nfour", 17),
    ("a\nbb\nccc", 6),
    ("a\n\nbb", 3),
    ("héllo\nwörld", 7),
    ("\n\n\n", 2),
]

INPUT_CASES: list = [
    "abc",
    "",
    97,
    [104, 105],
    "héllo",
    "😀",
    [128512],
]


def build_helper_fixtures() -> dict:
    from gbnf.grammar_graph.get_input_as_code_points import get_input_as_code_points
    from gbnf.utils.errors.build_error_position import build_error_position
    from gbnf.utils.errors.get_input_as_string import get_input_as_string
    from gbnf.utils.is_point_in_range import is_point_in_range

    error_positions = []
    for src, pos in ERROR_POSITION_CASES:
        entry: dict = {"src": src, "pos": pos}
        try:
            entry["lines"] = build_error_position(src, pos)
        except Exception as err:  # noqa: BLE001
            entry["lines"] = None
            entry["error"] = serialize_error(err)
        error_positions.append(entry)

    inputs = []
    for src in INPUT_CASES:
        inputs.append(
            {
                "input": src,
                "asString": get_input_as_string(src),
                "asCodePoints": get_input_as_code_points(src),
            },
        )

    point_ranges = []
    for point, given_range in [
        (97, (97, 122)),
        (122, (97, 122)),
        (96, (97, 122)),
        (123, (97, 122)),
        (5, (5, 5)),
    ]:
        point_ranges.append(
            {
                "point": point,
                "range": list(given_range),
                "result": is_point_in_range(point, given_range),
            },
        )

    return {
        "errorPositions": error_positions,
        "inputs": inputs,
        "pointRanges": point_ranges,
    }


def main() -> None:
    fixtures = {
        "description": (
            "Generated from reference_implementation by generate_fixtures.py; "
            "do not edit by hand."
        ),
        "cases": [
            *(build_case(name, grammar, seqs) for name, grammar, seqs in CASES),
            *build_fuzz_cases(),
            *build_grammar_fuzz_cases(),
        ],
        "helpers": build_helper_fixtures(),
    }
    out = Path(__file__).with_name("fixtures.json")
    out.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({len(fixtures['cases'])} cases)")  # noqa: T201


if __name__ == "__main__":
    main()
