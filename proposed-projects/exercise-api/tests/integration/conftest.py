import json
from pathlib import Path

import pytest

# Fixture ports do not parse GBNF. A grammar starting with "bad" is a grammar error at
# pos 3; input characters outside "ab" are an input error at their index; otherwise the
# state yields one char rule per input character plus an end rule.

PYTHON_REFERENCE = '''
class GrammarParseError(Exception):
    def __init__(self, grammar, pos):
        super().__init__(grammar)
        self.pos = pos


class InputParseError(Exception):
    def __init__(self, text, pos):
        super().__init__(text)
        self.pos = pos


class RuleChar:
    def __init__(self, value):
        self.value = value


class RuleEnd:
    pass


class State:
    def __init__(self, text):
        self.text = text

    def add(self, text):
        for index, char in enumerate(text):
            if char not in "ab":
                raise InputParseError(text, index)
        return State(self.text + text)

    def __iter__(self):
        for char in self.text:
            yield RuleChar([ord(char)])
        yield RuleEnd()


def GBNF(grammar, initial=""):
    if grammar.startswith("bad"):
        raise GrammarParseError(grammar, 3)
    return State("").add(initial)
'''

PYTHON_PLAIN_DICTS = PYTHON_REFERENCE.replace(
    "            yield RuleChar([ord(char)])\n        yield RuleEnd()",
    '            yield {"type": "char", "value": [ord(char)]}\n        yield {"type": "end"}',
)

PYTHON_OFF_BY_ONE = PYTHON_REFERENCE.replace("raise InputParseError(text, index)", "raise InputParseError(text, index + 1)")

PYTHON_ALLOCATING = PYTHON_REFERENCE.replace(
    "        return State(self.text + text)",
    "        if text == 'abab':\n            chunks = []\n            while True:\n                chunks.append(bytearray(1 << 30))\n        return State(self.text + text)",
)

PYTHON_SLEEPING = PYTHON_REFERENCE.replace(
    "        return State(self.text + text)",
    "        if text == 'abab':\n            __import__('time').sleep(60)\n        return State(self.text + text)",
)

PYTHON_EXITING = PYTHON_REFERENCE.replace("        return State(self.text + text)", "        if text == 'abab':\n            raise SystemExit(3)\n        return State(self.text + text)")

TYPESCRIPT_REFERENCE = """
export class GrammarParseError extends Error {
  pos: number;
  constructor(grammar: string, pos: number) { super(grammar); this.pos = pos; }
}
export class InputParseError extends Error {
  pos: number;
  constructor(text: string, pos: number) { super(text); this.pos = pos; }
}
class RuleChar { type = "char"; constructor(public value: number[]) {} }
class RuleEnd { type = "end"; }
class State {
  constructor(private text: string) {}
  add(text: string): State {
    for (let i = 0; i < text.length; i++) {
      if (!"ab".includes(text[i])) throw new InputParseError(text, i);
    }
    return new State(this.text + text);
  }
  *[Symbol.iterator]() {
    for (const c of this.text) yield new RuleChar([c.charCodeAt(0)]);
    yield new RuleEnd();
  }
}
export const GBNF = (grammar: string, initial = "") => {
  if (grammar.startsWith("bad")) throw new GrammarParseError(grammar, 3);
  return new State("").add(initial);
};
export default GBNF;
"""

TYPESCRIPT_PLAIN_OBJECTS = TYPESCRIPT_REFERENCE.replace(
    "    for (const c of this.text) yield new RuleChar([c.charCodeAt(0)]);\n    yield new RuleEnd();",
    '    for (const c of this.text) yield { type: "char", value: [c.charCodeAt(0)] };\n    yield { type: "end" };',
)

TYPESCRIPT_NAMED_ONLY = TYPESCRIPT_REFERENCE.replace("export default GBNF;\n", "")

TYPESCRIPT_ALLOCATING = TYPESCRIPT_REFERENCE.replace(
    "    return new State(this.text + text);",
    '    if (text === "abab") { const chunks = []; while (true) chunks.push(new Uint8Array(1 << 30)); }\n    return new State(this.text + text);',
)

TYPESCRIPT_OFF_BY_ONE = TYPESCRIPT_REFERENCE.replace("throw new InputParseError(text, i);", "throw new InputParseError(text, i + 1);")

CASES = [
    {"grammar": 'root ::= "a"', "input": "ab"},
    {"grammar": 'root ::= "a"', "input": ""},
    {"grammar": 'root ::= "a"', "input": "abab"},
    {"grammar": 'root ::= "a"', "input": "axb"},
    {"grammar": 'bad ::= "a"', "input": "a"},
]
OFF_BY_ONE_DISAGREEMENTS = 1

LADDER_CASES = [
    {"grammar": 'root ::= "a"', "input": "a", "rung": "1-one"},
    {"grammar": 'root ::= "a"', "input": "ab", "rung": "2-two"},
    {"grammar": 'root ::= "a"', "input": "abab", "rung": "3-four"},
    {"grammar": 'root ::= "a"', "input": "axb", "rung": "4-raises"},
]
LADDER_RUNGS = ["1-one", "2-two", "3-four"]
LADDER_BUDGET_CASES = [
    {**LADDER_CASES[0], "repeat": 1, "warmup": 0},
    {**LADDER_CASES[1], "repeat": 8, "warmup": 2},
    {**LADDER_CASES[2], "repeat": 8, "warmup": 2},
    LADDER_CASES[3],
]


def _python_package(root: Path, source: str) -> Path:
    (root / "gbnf").mkdir(parents=True)
    (root / "gbnf" / "__init__.py").write_text(source)
    return root


def _python_flat(root: Path, source: str) -> Path:
    errors, rest = source.split("\n\n\nclass RuleChar", 1)
    root.mkdir(parents=True)
    (root / "__init__.py").write_text("from .gbnf import GBNF, GrammarParseError, InputParseError\n")
    (root / "errors.py").write_text(errors)
    (root / "gbnf.py").write_text("from .errors import GrammarParseError, InputParseError\n\n\nclass RuleChar" + rest)
    return root


def _typescript(root: Path, source: str) -> Path:
    (root / "src").mkdir(parents=True)
    (root / "src" / "index.ts").write_text(source)
    return root


@pytest.fixture
def cases_file(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text("".join(json.dumps(case) + "\n" for case in CASES))
    return path


@pytest.fixture
def ladder_cases_file(tmp_path):
    path = tmp_path / "ladder.jsonl"
    path.write_text("".join(json.dumps(case) + "\n" for case in LADDER_CASES))
    return path


@pytest.fixture
def ladder_budget_cases_file(tmp_path):
    path = tmp_path / "ladder-budgets.jsonl"
    path.write_text("".join(json.dumps(case) + "\n" for case in LADDER_BUDGET_CASES))
    return path


@pytest.fixture
def python_reference(tmp_path):
    return _python_package(tmp_path / "python_reference", PYTHON_REFERENCE)


@pytest.fixture
def python_plain_dicts(tmp_path):
    return _python_package(tmp_path / "python_plain_dicts", PYTHON_PLAIN_DICTS)


@pytest.fixture
def python_off_by_one(tmp_path):
    return _python_package(tmp_path / "python_off_by_one", PYTHON_OFF_BY_ONE)


@pytest.fixture
def python_allocating(tmp_path):
    return _python_package(tmp_path / "python_allocating", PYTHON_ALLOCATING)


@pytest.fixture
def python_sleeping(tmp_path):
    return _python_package(tmp_path / "python_sleeping", PYTHON_SLEEPING)


@pytest.fixture
def python_exiting(tmp_path):
    return _python_package(tmp_path / "python_exiting", PYTHON_EXITING)


@pytest.fixture
def python_flat(tmp_path):
    return _python_flat(tmp_path / "python_flat", PYTHON_REFERENCE)


@pytest.fixture
def typescript_reference(tmp_path):
    return _typescript(tmp_path / "typescript_reference", TYPESCRIPT_REFERENCE)


@pytest.fixture
def typescript_plain_objects(tmp_path):
    return _typescript(tmp_path / "typescript_plain_objects", TYPESCRIPT_PLAIN_OBJECTS)


@pytest.fixture
def typescript_named_only(tmp_path):
    return _typescript(tmp_path / "typescript_named_only", TYPESCRIPT_NAMED_ONLY)


@pytest.fixture
def typescript_allocating(tmp_path):
    return _typescript(tmp_path / "typescript_allocating", TYPESCRIPT_ALLOCATING)


@pytest.fixture
def typescript_off_by_one(tmp_path):
    return _typescript(tmp_path / "typescript_off_by_one", TYPESCRIPT_OFF_BY_ONE)


@pytest.fixture
def grammars_dir(tmp_path):
    directory = tmp_path / "grammars"
    directory.mkdir()
    (directory / "simple.gbnf").write_text('root ::= "a"\n')
    (directory / "simple.json").write_text(json.dumps(["a", "ab"]))
    return directory
