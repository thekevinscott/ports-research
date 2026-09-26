"""Deterministic pseudo-random corpus used by the differential tests.

The cases are generated (rather than stored) so the committed golden file only has
to hold the reference implementation's answers. The seed is fixed, so the same
cases are produced on every run and on every machine.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

SEED = 20260908

GRAMMARS: Dict[str, str] = {
    "json": (
        'root ::= object\n'
        'object ::= "{" ws ( string ":" ws value ( "," ws string ":" ws value )* )? "}" ws\n'
        'value ::= object | array | string | number | ("true" | "false" | "null") ws\n'
        'array ::= "[" ws ( value ( "," ws value )* )? "]" ws\n'
        'string ::= "\\"" ( [^"\\\\] )* "\\"" ws\n'
        'number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ws\n'
        'ws ::= ([ \\t\\n] ws)?'
    ),
    "nested": 'root ::= (("a" | "b") "c")+ "d"',
    "recursive": 'root ::= "(" root ")" | "x"',
    "list": 'root ::= item+\nitem ::= "- " [a-z]+ "\\n"',
    "csv": 'root ::= row+\nrow ::= field ("," field)* "\\n"\nfield ::= [a-zA-Z0-9]*',
    "quant": 'root ::= "a"* "b"? [c-e]+ "f"',
}

ALPHABETS: Dict[str, str] = {
    "json": '{}[]",:0123456789abcnulltrfse. \n',
    "nested": "abcd",
    "recursive": "()x",
    "list": "- abc\n",
    "csv": "ab1,\n",
    "quant": "abcdef",
}


def build_cases() -> List[Dict[str, Any]]:
    rng = random.Random(SEED)
    cases: List[Dict[str, Any]] = []
    for name, grammar in GRAMMARS.items():
        alphabet = ALPHABETS[name]
        for i in range(60):
            length = rng.randint(1, 12)
            text = "".join(rng.choice(alphabet) for _ in range(length))
            cases.append({"name": f"fuzz-{name}-{i}", "grammar": grammar, "inputs": [text]})
        for i in range(25):
            steps = [
                "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4)))
                for _ in range(rng.randint(2, 5))
            ]
            cases.append(
                {"name": f"fuzz-steps-{name}-{i}", "grammar": grammar, "steps": steps}
            )
    return cases
