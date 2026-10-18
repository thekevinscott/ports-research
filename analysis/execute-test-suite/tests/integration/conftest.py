import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from gbnf_experiment.config import GBNF_COMMIT, PREPARE_DOCKER_DIRECTORY, compute_prepare_cache_key
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

from execute_test_suite.cli import cli

PYTHON_TEST_BODY = (
    "\n\ndef describe_gbnf():\n"
    "    def it_adds_input_and_compares_errors():\n"
    "        assert [*(GBNF('root ::= \"a\"') + 'a')] == [42]\n"
    "        assert InputParseError('a', 1) == InputParseError('a', 1)\n"
)
PYTHON_INTEGRATION_TEST = "from gbnf import GBNF, InputParseError\n" + PYTHON_TEST_BODY
PYTHON_UNIT_TEST = "from . import GBNF, InputParseError\n" + PYTHON_TEST_BODY
PYTHON_NESTED_UNIT_TEST = (
    "from .rule import RULE\n\n\n"
    "def describe_rule():\n"
    "    def it_is_the_expected_value():\n"
    "        assert RULE == 42\n"
)

TYPESCRIPT_TEST_BODY = (
    'describe("GBNF", () => {\n'
    '  it("returns the expected value", () => {\n'
    "    expect(GBNF()).toBe(42);\n"
    "  });\n"
    "});\n"
)
TYPESCRIPT_INTEGRATION_TEST = 'import GBNF from "gbnf";\n\n' + TYPESCRIPT_TEST_BODY
TYPESCRIPT_UNIT_TEST = 'import GBNF from "./index.js";\n\n' + TYPESCRIPT_TEST_BODY

# Colocated unit tests and two generated integration tests per language, at the paths
# the prepared reference trees use, beside a reference source that is never staged.
REFERENCE_TREES = {
    "python": {
        "gbnf/__init__.py": "raise ImportError('the reference source is never graded')\n",
        "gbnf/gbnf_test.py": PYTHON_UNIT_TEST,
        "gbnf/rules/rule_test.py": PYTHON_NESTED_UNIT_TEST,
        "tests/generated/iteration/iteration_test.py": PYTHON_INTEGRATION_TEST,
        "tests/generated/validation/validation_test.py": PYTHON_INTEGRATION_TEST,
    },
    "javascript": {
        "src/index.ts": 'throw new Error("the reference source is never graded");\n',
        "src/gbnf.test.ts": TYPESCRIPT_UNIT_TEST,
        "integration-tests/generated/iteration/iteration.test.ts": TYPESCRIPT_INTEGRATION_TEST,
        "integration-tests/generated/validation/validation.test.ts": TYPESCRIPT_INTEGRATION_TEST,
    },
}

PYTHON_PACKAGE_PORT = (
    "class InputParseError(Exception):\n"
    "    def __eq__(self, other):\n"
    "        return type(self) is type(other) and self.args == other.args\n\n"
    "    __hash__ = Exception.__hash__\n\n\n"
    "class State:\n"
    "    def __init__(self, value):\n"
    "        self.value = value\n\n"
    "    def add(self, text):\n"
    "        return State(self.value)\n\n"
    "    def __add__(self, text):\n"
    "        return self.add(text)\n\n"
    "    def __iter__(self):\n"
    "        yield self.value\n\n\n"
    "def GBNF(grammar, initial=''):\n"
    "    return State({value})\n"
)

PYTHON_FLAT_INIT = "from .gbnf import GBNF, InputParseError\n"
PYTHON_FLAT_GBNF = (
    "from .errors import InputParseError\n\n\n"
    "class State:\n"
    "    def add(self, text):\n"
    "        return State()\n\n"
    "    def __iter__(self):\n"
    "        yield 42\n\n\n"
    "def GBNF(grammar, initial=''):\n"
    "    return State()\n"
)
PYTHON_FLAT_ERRORS = "class InputParseError(Exception):\n    pass\n"

PYTHON_UNIMPORTED_MODULE = (
    "def never_called(value):\n"
    "    doubled = value * 2\n"
    "    return doubled\n"
)

TYPESCRIPT_UNCALLED_EXPORT = (
    "export function neverCalled(): number {\n"
    "  const doubled = 2 * 2;\n"
    "  return doubled;\n"
    "}\n\n"
    "export default function GBNF(): number {\n"
    "  return 42;\n"
    "}\n"
)


def write_tree(directory: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        (directory / relative).parent.mkdir(parents=True, exist_ok=True)
        (directory / relative).write_text(text)
    return directory


@pytest.fixture(autouse=True)
def prepared_directory(tmp_path):
    """Synthetic prepared reference trees, at the keys the CLI computes, under a patched
    `PREPARED_DIRECTORY`.

    The CLI takes no parameter for the prepared tree's location, so the constant is
    patched where locate_test_suite binds it; the same carve-out gbnf_experiment's own
    tests/integration/conftest.py takes for the same field.
    """
    directory = tmp_path / "prepared"
    for tree, files in REFERENCE_TREES.items():
        key = compute_prepare_cache_key(
            GBNF_COMMIT,
            PREPARE_DOCKER_DIRECTORY,
            assemble_whitelist(
                tree,
                include_unit_tests=True,
                include_source_integration_tests=True,
                include_target_integration_tests=False,
            ),
        )
        write_tree(directory / key / tree, files)
    with patch("execute_test_suite.locate_test_suite.PREPARED_DIRECTORY", directory):
        yield directory


@pytest.fixture
def invoke():
    """Runs the CLI on one target and suite, returning click's result."""

    def run(language, target, suite, *flags):
        return CliRunner().invoke(
            cli, ["--language", language, "--target", str(target), "--suite", suite, *flags]
        )

    return run


@pytest.fixture
def grade(invoke):
    """Runs the CLI on one target and suite, returning the JSON report it printed."""
    return lambda *args: json.loads(invoke(*args).output)


@pytest.fixture
def python_target(tmp_path):
    """A `gbnf/` package laid out as the reference is, whose state supports `+` and
    whose error compares by value."""

    def build(value: int) -> Path:
        return write_tree(
            tmp_path / f"python_target_{value}",
            {
                "gbnf/__init__.py": PYTHON_PACKAGE_PORT.format(value=value),
                "gbnf/rules/__init__.py": "",
                "gbnf/rules/rule.py": f"RULE = {value}\n",
            },
        )

    return build


@pytest.fixture
def python_unsplit_target(tmp_path):
    """A passing `gbnf/` package with no `rules` subpackage for the nested unit test."""
    return write_tree(
        tmp_path / "python_unsplit_target",
        {"gbnf/__init__.py": PYTHON_PACKAGE_PORT.format(value=42)},
    )


@pytest.fixture
def python_flat_target(tmp_path):
    """A flat `gbnf.py` with relative imports, an `add`-only state and a bare exception."""
    return write_tree(
        tmp_path / "python_flat_target",
        {
            "__init__.py": PYTHON_FLAT_INIT,
            "gbnf.py": PYTHON_FLAT_GBNF,
            "errors.py": PYTHON_FLAT_ERRORS,
        },
    )


@pytest.fixture
def python_nested_target(tmp_path):
    """A passing `gbnf/` package one directory below the target root, where the suite
    never finds it."""
    return write_tree(
        tmp_path / "python_nested_target",
        {"python/gbnf/__init__.py": PYTHON_PACKAGE_PORT.format(value=42)},
    )


@pytest.fixture
def python_partial_target(python_target):
    """A passing port carrying a module the suite never imports."""
    return write_tree(python_target(42), {"unused.py": PYTHON_UNIMPORTED_MODULE})


@pytest.fixture
def typescript_target(tmp_path):
    def build(value: int) -> Path:
        return write_tree(
            tmp_path / f"typescript_target_{value}",
            {"src/index.ts": f"export default function GBNF(): number {{ return {value}; }}\n"},
        )

    return build


@pytest.fixture
def typescript_relocated_target(tmp_path):
    """A passing port whose entry is not at `src/index.ts`, where the unit test imports it."""
    return write_tree(
        tmp_path / "typescript_relocated_target",
        {"lib/index.ts": "export default function GBNF(): number { return 42; }\n"},
    )


@pytest.fixture
def typescript_nested_target(tmp_path):
    """A passing port one directory below the target root, where the suite never finds it."""
    return write_tree(
        tmp_path / "typescript_nested_target",
        {"javascript/src/index.ts": "export default function GBNF(): number { return 42; }\n"},
    )


@pytest.fixture
def typescript_partial_target(tmp_path):
    """A passing port whose entry file exports a function the suite never calls."""
    return write_tree(
        tmp_path / "typescript_partial_target", {"src/index.ts": TYPESCRIPT_UNCALLED_EXPORT}
    )


@pytest.fixture
def typescript_unresolvable_tsconfig_target(typescript_target):
    """A passing port whose tsconfig extends a file that is not on disk.

    The hand-written typescript reference is shaped this way: its tsconfig extends the
    monorepo root's, which the prepared tree does not carry.
    """
    return write_tree(
        typescript_target(42),
        {
            "tsconfig.json": (
                '{"extends": "../../../tsconfig.json", "compilerOptions": {"target": "esnext"}}\n'
            )
        },
    )


@pytest.fixture
def typescript_named_target(tmp_path):
    """Exports `GBNF` by name only, with no default export."""
    return write_tree(
        tmp_path / "typescript_named_target",
        {"src/index.ts": "export function GBNF(): number { return 42; }\n"},
    )
