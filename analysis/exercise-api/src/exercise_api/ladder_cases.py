import json
import string
from pathlib import Path

ALTERNATIVES = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
REPETITION_LENGTHS = [16, 64, 256, 16384, 65536]
MIXED_UNITS = ["a", "Z", "0", "_", "é", "日", "本", "\t", "\n", " "]
MIXED_LENGTH = 256
CHAIN_SIZES = [32, 128, 512]
FLAT_SIZES = [1024, 4096, 16384, 65536]
# Depth 32768 is left out: one pass costs the typescript reference over 75 s, so a
# warm-up plus one timed pass does not fit the 600 s the whole list gets.
DEPTHS = [8, 32, 128, 512, 2048, 8192]
LITERAL = 'root ::= "a"\n'
ALTERNATION = "root ::= " + " | ".join(f'"{name}"' for name in ALTERNATIVES) + "\n"
REPETITION = "root ::= [a-z]+\n"
CHARACTER_CLASSES = "root ::= ([a-zA-Z0-9_] | [^\\x00-\\x7F] | [\\t\\n ])+\n"

# The driver timeout is one budget for the whole list, so the slowest case caps the
# repeat count of every other one. Each case carries its own instead, sized from the
# reference cost of one pass: the sub-100 ms cases can afford 100, the seconds-long
# ones cannot.
BUDGETS = {"fast": {"warmup": 3, "repeat": 100}, "slow": {"warmup": 1, "repeat": 5}, "slowest": {"warmup": 0, "repeat": 1}}
SLOW_INPUT_LENGTHS = {("3-repetition", 16384), ("3-repetition", 65536), ("7-json", 16384), ("7-json", 65536), ("8-json-depth", 4102)}
SLOWEST_INPUT_LENGTHS = {("8-json-depth", 16390)}


def _budget(rung: str, input_len: int) -> dict:
    key = (rung, input_len)
    if key in SLOWEST_INPUT_LENGTHS:
        return BUDGETS["slowest"]
    return BUDGETS["slow" if key in SLOW_INPUT_LENGTHS else "fast"]


def _rule_name(index: int) -> str:
    """Letters only: the reference's grammar parser stops at the digit in a name like `r1`."""
    return "r" + string.ascii_lowercase[index // 26] + string.ascii_lowercase[index % 26]


def _chain(rules: int) -> str:
    return (
        f"root ::= {_rule_name(0)}\n"
        + "".join(f'{_rule_name(i)} ::= "x" {_rule_name(i + 1)}\n' for i in range(rules - 1))
        + f'{_rule_name(rules - 1)} ::= "leaf"\n'
    )


def _mixed(length: int) -> str:
    return "".join(MIXED_UNITS[index % len(MIXED_UNITS)] for index in range(length))


def _flat_object(size: int) -> str:
    pairs: list[str] = []
    used = 2
    while used + len(f'"k{len(pairs)}":"v{len(pairs)}"') + (1 if pairs else 0) <= size:
        used += len(f'"k{len(pairs)}":"v{len(pairs)}"') + (1 if pairs else 0)
        pairs.append(f'"k{len(pairs)}":"v{len(pairs)}"')
    pairs[-1] = pairs[-1][:-1] + "x" * (size - used) + '"'
    return "{" + ",".join(pairs) + "}"


def _nested(depth: int) -> str:
    """json.gbnf's root is an object, so the nesting hangs off one key."""
    return '{"a":' + "[" * depth + "]" * depth + "}"


def ladder_cases(grammars_dir: Path) -> list[dict]:
    arithmetic = (grammars_dir / "arithmetic.gbnf").read_text()
    arithmetic_inputs = json.loads((grammars_dir / "arithmetic.json").read_text())
    json_grammar = (grammars_dir / "json.gbnf").read_text()
    rungs = [
        ("1-literal", [(LITERAL, "a")]),
        ("2-alternation", [(ALTERNATION, ALTERNATIVES[-1])]),
        ("3-repetition", [(REPETITION, "a" * length) for length in REPETITION_LENGTHS]),
        ("4-character-classes", [(CHARACTER_CLASSES, _mixed(MIXED_LENGTH))]),
        ("5-rule-references", [(_chain(rules), "x" * (rules - 1) + "leaf") for rules in CHAIN_SIZES]),
        ("6-arithmetic", [(arithmetic, max(arithmetic_inputs, key=len))]),
        ("7-json", [(json_grammar, _flat_object(size)) for size in FLAT_SIZES]),
        ("8-json-depth", [(json_grammar, _nested(depth)) for depth in DEPTHS]),
    ]
    return [
        {"grammar": grammar, "input": text, "rung": rung, **_budget(rung, len(text))}
        for rung, pairs in rungs
        for grammar, text in pairs
    ]
