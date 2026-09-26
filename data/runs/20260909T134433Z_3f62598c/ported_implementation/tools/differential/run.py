"""Differential test: run the same grammars and inputs through the reference
JavaScript implementation and this port, then compare the traces.

    python3 tools/differential/run.py [--grammars N] [--mutations N] [--seed N]

Requires node >= 22 (for --experimental-transform-types); the reference sources
are loaded straight from /workspace/reference_implementation/src.

Every difference is classified. Known, documented deviations (see README.md) are
reported separately from unexpected ones; the exit status is non-zero only when
an unexpected difference is found.
"""

import argparse
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(HERE, ".work")
sys.path.insert(0, ROOT)

from tests.helpers import load_fixture  # noqa: E402

GRAMMAR_CHARS = list('abz09 \t\n:=|()[]*+?^-"\\#/xuU{}')
INPUT_CHARS = list('abfoszAZ019 +-*/=()[]{}\n\t"\\') + ["é"]

# Deviations from the reference that the port makes on purpose.
KNOWN = {
    "missing-root": "SymbolIds does not contain key: root",
    "sparse-hole": "rule is not iterable",
}


def unescape(value: str) -> str:
    return value.replace("\\n", "\n").replace("\\t", "\t")


def base_grammars() -> list:
    grammars = []
    valid, invalid = load_fixture("validate-grammar")
    grammars.extend(valid)
    grammars.extend(g for g, _pos, _reason in invalid)
    valid_input, invalid_input = load_fixture("validate-input")
    grammars.extend(g for g, _i in valid_input)
    grammars.extend(g for g, _i, _p in invalid_input)
    (iteration,) = load_fixture("iteration")
    grammars.extend(g for g, _e in iteration)
    (initial,) = load_fixture("iteration-with-an-initial-string")
    grammars.extend(g for g, _i, _e in initial)
    throwing, parsing, _errors = load_fixture("iteration-with-additional-strings")
    grammars.extend(g for g, _s, _a in throwing)
    grammars.extend(g for g, _s, _a, _e in parsing)
    (known,) = load_fixture("grammars")
    grammars.extend(unescape(g) for _n, _t, g in known)
    grammars.extend(
        [
            "",
            "   ",
            "# just a comment\n",
            '# leading comment\nroot ::= "foo" # trailing comment\n',
            'root ::= "a\\tb\\nc\\rd"',
            'root ::= "\\x41\\u0041\\U0001F4A9\\\\\\""',
            "root ::= [\\[\\]]",
            "root ::= [a-]",
            "root ::= [-a]",
            "root ::= [a-cx-z]",
            "root ::= [^a-cx-z0]",
            'root ::= ("a" | "b") ("c" | "d")',
            'root ::= ("a" ("b" ("c")?)*)+',
            'root ::= a+ b?\na ::= "a"\nb ::= "b"',
            'root ::= ""',
            "root ::= foo\n",
            "root ::= *",
            'root ::= ("a"',
            'root ::= "unterminated',
            "root ::= [abc",
            'root ::= "a"\r\nfoo ::= "b"',
            'root ::= "\\q"',
            "root ::= 1",
        ]
    )
    seen = set()
    unique = []
    for grammar in grammars:
        if grammar not in seen:
            seen.add(grammar)
            unique.append(grammar)
    return unique


def mutate(grammar: str, rng: random.Random) -> str:
    chars = list(grammar)
    for _ in range(rng.randint(1, 4)):
        if not chars:
            chars = list('root ::= "a"')
        op = rng.choice(["del", "ins", "sub"])
        i = rng.randrange(len(chars))
        if op == "del":
            del chars[i]
        elif op == "ins":
            chars.insert(i, rng.choice(GRAMMAR_CHARS))
        else:
            chars[i] = rng.choice(GRAMMAR_CHARS)
    return "".join(chars)


def build_corpus(grammar_limit: int, mutations: int, seed: int) -> list:
    rng = random.Random(seed)
    cases = []

    def inputs_for(count: int, max_len: int) -> list:
        return [
            "".join(rng.choice(INPUT_CHARS) for _ in range(rng.randint(1, max_len)))
            for _ in range(count)
        ]

    for grammar in base_grammars()[:grammar_limit]:
        cases.append(
            {
                "grammar": grammar,
                "inputs": ["", "f", "foo", "bar", "1+2=3\n"] + inputs_for(8, 12),
            }
        )
        for _ in range(mutations):
            cases.append(
                {
                    "grammar": mutate(grammar, rng),
                    "inputs": ["", "f", "a1", "1+2=3\n"] + inputs_for(4, 6),
                }
            )
    return cases


def classify(reference: dict, ported: dict) -> str:
    message = (reference.get("construct") or {}).get("message", "")
    for label, needle in KNOWN.items():
        if message == needle:
            return label
    if "call stack" in message:
        return "stack-overflow"
    if "Invalid escape sequence" in (ported.get("construct") or {}).get("message", ""):
        return "nan-escape"
    if "😀" in json.dumps(ported, ensure_ascii=False):
        return "astral-input"
    return "unexpected"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grammars", type=int, default=200)
    parser.add_argument("--mutations", type=int, default=4)
    parser.add_argument("--seed", type=int, default=987654)
    args = parser.parse_args()

    os.makedirs(WORK, exist_ok=True)
    cases = build_corpus(args.grammars, args.mutations, args.seed)
    with open(os.path.join(WORK, "corpus.json"), "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False)
    print(
        f"corpus: {len(cases)} grammars, "
        f"{sum(len(c['inputs']) for c in cases)} inputs"
    )

    subprocess.run(["node", os.path.join(HERE, "prepare.mjs")], check=True)
    subprocess.run(
        [
            "node",
            "--experimental-transform-types",
            "--import",
            os.path.join(HERE, "register.mjs"),
            os.path.join(HERE, "run_js.mjs"),
        ],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run([sys.executable, os.path.join(HERE, "run_py.py")], check=True)

    with open(os.path.join(WORK, "out-js.json"), encoding="utf-8") as fh:
        reference_traces = json.load(fh)
    with open(os.path.join(WORK, "out-py.json"), encoding="utf-8") as fh:
        ported_traces = json.load(fh)

    counts: dict = {}
    unexpected = []
    for reference, ported in zip(reference_traces, ported_traces):
        if reference == ported:
            continue
        label = classify(reference, ported)
        counts[label] = counts.get(label, 0) + 1
        if label == "unexpected":
            unexpected.append((reference, ported))

    identical = sum(1 for a, b in zip(reference_traces, ported_traces) if a == b)
    print(f"identical traces: {identical} of {len(reference_traces)}")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")

    for reference, ported in unexpected[:10]:
        print("---")
        print(f"grammar: {reference['grammar']!r}")
        print(f"  reference: {reference['construct']!r}")
        print(f"  port:      {ported['construct']!r}")

    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
