"""Record the behaviour of reference_implementation/ so the port can be diffed against it.

Run from the repository root:

    python3 ported_implementation/tests/parity/generate_fixtures.py

The companion `parity.test.ts` replays the exact same driver against
ported_implementation/ and asserts the recorded values match.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "reference_implementation"))

from gbnf import GBNF  # noqa: E402
from gbnf.grammar_parser.build_rule_stack import build_rule_stack  # noqa: E402
from gbnf.rules_builder import RulesBuilder  # noqa: E402

GRAMMARS = [
    'root ::= "foo"',
    'root ::= "\\""',
    'root ::= foo\n            foo ::= "bar"',
    'root ::= foo-bar\n            foo-bar ::= "bar"',
    "root  ::= [\u3041-\u309f]",
    "root  ::= [az]",
    "root  ::= [a-zA-Z0-9]",
    "root  ::= [a-z-]",
    'root  ::= "f" ("b" | "a")',
    'root  ::= "f"?',
    'root  ::= "f"*',
    'root  ::= "f"+',
    "root  ::= [a-zA-Z0-9]*",
    'root  ::= "f" ("b" | "a")*',
    "root ::= [^\\n]",
    "root ::= [^0-9]",
    'root ::= [^\\n]+ "\\n"',
    'root ::= "\\"" ( [^"abcdefgh])* ',
    'root ::= "\\"" ( [^"abcdefghA-Z])* ',
    'root ::= "\\x2A" "\\u006F" "\\U0001F4A9" "\\t" "\\n" "\\r" "\\"" "\\[" "\\]" "\\\\"',
    'root ::= "\\x2A" "\\u006F" "\\U0001F4A9" "\\t" "\\n" "\\r" "\\"" "\\[" "\\]" "\\\\" (\n'
    '                "\\x2A" | "\\u006F" | "\\U0001F4A9" | "\\t" | "\\n" | "\\r" | "\\"" | "\\[" | "\\]"  | "\\\\" )',
    '\n            root ::= (expr "=" term "\\n")+\n'
    "            expr ::= term ([-+*/] term)*\n"
    "            term ::= [0-9]+\n            ",
    "\n            root ::= [a-z0-9_]*\n            ",
    "\n            root ::= [a-z] [a-z0-9_]*\n            ",
    "\n            root ::= ident\n            ident ::= [a-z] [a-z0-9_]* ws\n"
    "            ws ::= [ \\t\\n]*\n            ",
    '\n            root  ::= (expr "=" ws term "\\n")+\n'
    "            expr  ::= term ([-+*/] term)*\n"
    '            term  ::= ident | num | "(" ws expr ")" ws\n'
    "            ident ::= [a-z] [a-z0-9_]* ws\n"
    "            num   ::= [0-9]+ ws\n"
    "            ws    ::= [ \\t\\n]*\n            ",
    '\n            root ::=\n            "\\"" (\n'
    '                [^"\\\\\\x7F\\x00-\\x1F] |\n'
    '                "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes\n'
    '            )* "\\""\n            ',
    "\n            root   ::= object\n"
    '            value  ::= object | array | string | number | ("true" | "false" | "null") ws\n'
    "            object ::=\n"
    '              "{" ws (\n'
    '                        string ":" ws value\n'
    '                ("," ws string ":" ws value)*\n'
    '              )? "}" ws\n'
    "            array  ::=\n"
    '              "[" ws (\n'
    "                        value\n"
    '                ("," ws value)*\n'
    '              )? "]" ws\n'
    "                  string ::=\n"
    '              "\\"" (\n'
    '                [^"\\\\\\x7F\\x00-\\x1F] |\n'
    '                "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes\n'
    '              )* "\\"" ws\n'
    '            number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws\n'
    "            # Optional space: by convention, applied in this grammar after literal chars when allowed\n"
    "            ws ::= ([ \\t\\n] ws)?\n            ",
    "\n            # A probably incorrect grammar for Japanese\n"
    "            root        ::= jp-char+ ([ \\t\\n] jp-char+)*\n"
    "            jp-char     ::= hiragana | katakana | punctuation | cjk\n"
    "            hiragana    ::= [\u3041-\u309f]\n"
    "            katakana    ::= [\u30a1-\u30ff]\n"
    "            punctuation ::= [\u3001-\u303e]\n"
    "            cjk         ::= [\u4e00-\u9fff]\n            ",
]

INVALID_GRAMMARS = [
    "",
    "   ",
    "root ::= foo",
    "root ::= ",
    "root",
    'root :: = "foo"',
    '123 ::= "foo"',
    'root ::= "foo" | ',
    'root ::= ("foo"',
    "root ::= *",
    "# just a comment\n",
    'foo ::= "bar"',
]

STEPS = 24


def serialize_value(value):
    if isinstance(value, (list, tuple)):
        return [serialize_value(v) for v in value]
    return value


def serialize_obj(obj):
    entry = {"t": type(obj).__name__}
    value = getattr(obj, "value", None)
    if value is not None:
        entry["v"] = serialize_value(value)
    return entry


def serialize_rules(state):
    # `RuleRef.nodes` is a Python set of identity-hashed nodes, so the order in
    # which the reference yields rules varies between runs. Sort so the fixture
    # captures the *set* of reachable rules rather than one run's ordering.
    return sorted(
        (serialize_obj(rule) for rule in state),
        key=lambda entry: json.dumps(entry, sort_keys=True),
    )


def pick_code_point(rules, prefer_last: bool):
    """Deterministically choose a code point accepted by one of `rules`.

    Both implementations run this identical algorithm, so the sequence of
    choices is itself part of what gets compared.
    """
    candidates = rules[::-1] if prefer_last else rules
    for rule in candidates:
        if rule["t"] == "RuleChar":
            values = rule["v"][::-1] if prefer_last else rule["v"]
            value = values[0]
            return value[1] if isinstance(value, list) else value
        if rule["t"] == "RuleCharExclude":
            span = range(126, 31, -1) if prefer_last else range(32, 127)
            for candidate in span:
                if not any(
                    (v[0] <= candidate <= v[1]) if isinstance(v, list) else v == candidate
                    for v in rule["v"]
                ):
                    return candidate
    return None


def walk(grammar: str, prefer_last: bool):
    steps = []
    try:
        state = GBNF(grammar)
    except Exception as e:  # noqa: BLE001
        return {"error": {"type": type(e).__name__, "message": str(e)}, "steps": steps}

    for _ in range(STEPS):
        rules = serialize_rules(state)
        step = {"rules": rules}
        steps.append(step)
        code_point = pick_code_point(rules, prefer_last)
        if code_point is None:
            break
        step["cp"] = code_point
        try:
            state = state.add(chr(code_point))
        except Exception as e:  # noqa: BLE001
            step["error"] = {"type": type(e).__name__, "message": str(e)}
            break
    return {"steps": steps}


def describe_grammar(grammar: str):
    entry = {"grammar": grammar}
    try:
        builder = RulesBuilder(grammar)
    except Exception as e:  # noqa: BLE001
        entry["builder_error"] = {"type": type(e).__name__, "message": str(e)}
        return entry

    entry["rules"] = [[serialize_obj(elem) for elem in rule] for rule in builder.rules]
    entry["symbol_ids"] = [[key, value] for key, value in builder.symbol_ids.items()]
    try:
        entry["stacked_rules"] = [
            [[serialize_obj(elem) for elem in path] for path in build_rule_stack(rule)]
            for rule in builder.rules
        ]
    except Exception as e:  # noqa: BLE001
        entry["stack_error"] = {"type": type(e).__name__, "message": str(e)}
    entry["walk_first"] = walk(grammar, prefer_last=False)
    entry["walk_last"] = walk(grammar, prefer_last=True)
    return entry


def main() -> None:
    fixtures = {
        "steps": STEPS,
        "grammars": [describe_grammar(grammar) for grammar in GRAMMARS],
        "invalid_grammars": [describe_grammar(grammar) for grammar in INVALID_GRAMMARS],
    }
    out = Path(__file__).with_name("fixtures.json")
    out.write_text(json.dumps(fixtures, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
