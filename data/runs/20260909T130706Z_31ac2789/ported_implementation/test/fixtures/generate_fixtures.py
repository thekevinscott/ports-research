"""Generate test fixtures from the Python reference implementation.

Run from the repository root:

    python3 ported_implementation/test/fixtures/generate_fixtures.py

The fixtures are consumed by `test/reference_parity.test.ts`, which asserts the
TypeScript port produces byte-for-byte identical results for the same inputs.
"""

import json
import sys
from pathlib import Path

REFERENCE = Path(__file__).resolve().parents[3] / "reference_implementation"
sys.path.insert(0, str(REFERENCE))

from gbnf import GBNF  # noqa: E402
from gbnf.grammar_graph.grammar_graph_types import (  # noqa: E402
    RuleChar,
    RuleCharExclude,
    RuleEnd,
)
from gbnf.grammar_graph.rule_ref import RuleRef  # noqa: E402
from gbnf.grammar_parser.build_rule_stack import build_rule_stack  # noqa: E402
from gbnf.rules_builder import RulesBuilder  # noqa: E402
from gbnf.rules_builder.rules_builder_types import (  # noqa: E402
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
)

INTERNAL_TYPES = {
    InternalRuleDefChar: "char",
    InternalRuleDefCharNot: "char_not",
    InternalRuleDefCharAlt: "char_alt",
    InternalRuleDefCharRngUpper: "char_rng_upper",
    InternalRuleDefReference: "rule_ref",
    InternalRuleDefAlt: "alt",
    InternalRuleDefEnd: "end",
}

RULE_TYPES = {
    RuleChar: "char",
    RuleCharExclude: "char_exclude",
    RuleEnd: "end",
    RuleRef: "ref",
}


def serialize_internal(rule):
    type_ = INTERNAL_TYPES[type(rule)]
    if hasattr(rule, "value"):
        return {"type": type_, "value": rule.value}
    return {"type": type_}


def serialize_rule(rule):
    type_ = RULE_TYPES[type(rule)]
    if hasattr(rule, "value"):
        return {"type": type_, "value": rule.value}
    return {"type": type_}


GRAMMARS = [
    'root ::= "foo"',
    'root ::= "\\""',
    "root ::= foo\n            foo ::= \"bar\"",
    "root ::= foo-bar\n            foo-bar ::= \"bar\"",
    "root  ::= [ぁ-ゟ]",
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
    'root ::= "foo" # a trailing comment\n',
    '# leading comment\nroot ::= "foo"\n',
    'root ::= "foo"\r\nfoo ::= "bar"\r\n',
    'root ::= "a" | "b" | "c"',
    'root ::= ("a" "b")+ "c"',
    'root ::= [a-z]* [0-9]?',
    'root ::= "\\x2A" "\\u006F" "\\U0001F4A9" "\\t" "\\n" "\\r" "\\"" "\\[" "\\]" "\\\\"',
    'root ::= "\\x2A" "\\u006F" "\\U0001F4A9" "\\t" "\\n" "\\r" "\\"" "\\[" "\\]" "\\\\" (\n'
    '                "\\x2A" | "\\u006F" | "\\U0001F4A9" | "\\t" | "\\n" | "\\r" | "\\"" | "\\[" | "\\]"  | "\\\\" )',
    "\n            root ::= (expr \"=\" term \"\\n\")+\n            expr ::= term ([-+*/] term)*\n"
    "            term ::= [0-9]+\n            ",
    "\n            root  ::= (expr \"=\" ws term \"\\n\")+\n            expr  ::= term ([-+*/] term)*\n"
    "            term  ::= ident | num | \"(\" ws expr \")\" ws\n            ident ::= [a-z] [a-z0-9_]* ws\n"
    "            num   ::= [0-9]+ ws\n            ws    ::= [ \\t\\n]*\n            ",
    "\n            root ::= [a-z0-9_]*\n            ",
    "\n            root ::= [a-z] [a-z0-9_]*\n            ",
    "\n            root ::= ident\n            ident ::= [a-z] [a-z0-9_]* ws\n            ws ::= [ \\t\\n]*\n"
    "            ",
    "\n            root ::=\n            \"\\\"\" (\n                [^\"\\\\\\x7F\\x00-\\x1F] |\n"
    "                \"\\\\\" ([\"\\\\/bfnrt] | \"u\" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes\n"
    "            )* \"\\\"\"\n            ",
    """
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
            string  ::=
              "\\"" (
                [^"\\\\] |
                "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
              )* "\\"" ws
            number  ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
            ws ::= ([ \\t\\n] ws)?
            """,
    """
            # A probably incorrect grammar for Japanese
            root        ::= jp-char+ ([ \\t\\n] jp-char+)*
            jp-char     ::= hiragana | katakana | punctuation | cjk
            hiragana    ::= [ぁ-ゟ]
            katakana    ::= [ァ-ヿ]
            punctuation ::= [、-〾]
            cjk         ::= [一-鿿]
            """,
]

# Grammars that are expected to blow up while parsing.
INVALID_GRAMMARS = [
    "",
    "root",
    "root ::=",
    'root ::= "foo',
    'root ::= foo',
    'foo ::= "bar"',
    'root ::= *',
    'root ::= ("a"',
    'root ::= [a',
    'root ::= "\\q"',
    '::= "foo"',
    'root ::= "a" "b" ]',
]

INPUTS = [
    "",
    "f",
    "fo",
    "foo",
    "foob",
    "b",
    "bar",
    "a",
    "ab",
    "abc",
    "z",
    "0",
    "9",
    "123",
    "1+2=3\n",
    "1+2",
    "-",
    "_",
    " ",
    "\n",
    "\t",
    '"',
    '"hello"',
    "{",
    '{"a":1}',
    "[",
    "[1,2]",
    "true",
    "null",
    "あ",
    "ア",
    "一",
    "、",
    "*",
    "o",
    "\r",
    "(",
    ")",
    "=",
]

# Sequences fed one chunk at a time, to exercise incremental parsing.
SEQUENCES = [
    ["f", "o", "o"],
    ["fo", "o"],
    ["a", "b", "c"],
    ["1", "+", "2", "=", "3", "\n"],
    ['"', "a", '"'],
    ["{", '"', "a"],
    ["a", "0", "_"],
]


def describe_error(err: Exception) -> dict:
    return {
        "error": type(err).__name__,
        "message": str(err),
    }


def build_case(grammar: str) -> dict:
    case: dict = {"grammar": grammar}
    try:
        rules_builder = RulesBuilder(grammar)
        case["rules"] = [
            [serialize_internal(rule) for rule in rule_list] for rule_list in rules_builder.rules
        ]
        case["symbolIds"] = dict(rules_builder.symbol_ids.items())
        case["stackedRules"] = [
            [[serialize_rule(rule) for rule in path] for path in build_rule_stack(rule_list)]
            for rule_list in rules_builder.rules
        ]
    except Exception as err:  # noqa: BLE001
        case["rulesError"] = describe_error(err)

    try:
        state = GBNF(grammar)
        case["initialRules"] = [serialize_rule(rule) for rule in state]
        case["size"] = state.size
    except Exception as err:  # noqa: BLE001
        case["initialError"] = describe_error(err)
        return case

    inputs = []
    for text in INPUTS:
        try:
            next_state = GBNF(grammar, text)
            inputs.append(
                {
                    "input": text,
                    "rules": [serialize_rule(rule) for rule in next_state],
                    "size": next_state.size,
                },
            )
        except Exception as err:  # noqa: BLE001
            inputs.append({"input": text, **describe_error(err)})
    case["inputs"] = inputs

    sequences = []
    for chunks in SEQUENCES:
        steps = []
        try:
            state = GBNF(grammar)
            for chunk in chunks:
                state = state.add(chunk)
                steps.append(
                    {
                        "chunk": chunk,
                        "rules": [serialize_rule(rule) for rule in state],
                        "size": state.size,
                    },
                )
        except Exception as err:  # noqa: BLE001
            steps.append(describe_error(err))
        sequences.append({"chunks": chunks, "steps": steps})
    case["sequences"] = sequences

    return case


def main() -> None:
    fixtures = {
        "grammars": [build_case(grammar) for grammar in GRAMMARS],
        "invalidGrammars": [build_case(grammar) for grammar in INVALID_GRAMMARS],
    }
    out = Path(__file__).parent / "reference_fixtures.json"
    out.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out} ({len(fixtures['grammars'])} grammars)")  # noqa: T201


if __name__ == "__main__":
    main()
