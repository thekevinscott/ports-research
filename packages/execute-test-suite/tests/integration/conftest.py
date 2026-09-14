from pathlib import Path
from unittest.mock import patch

import pytest
from gbnf_experiment.config import derivation_cache_key as DERIVATION_CACHE_KEY
from gbnf_experiment.config import settings


PYTHON_TEST = (
    "from gbnf import GBNF, InputParseError\n\n\n"
    "def describe_gbnf():\n"
    "    def it_adds_input_and_compares_errors():\n"
    "        assert [*(GBNF('root ::= \"a\"') + 'a')] == [42]\n"
    "        assert InputParseError('a', 1) == InputParseError('a', 1)\n"
)

TYPESCRIPT_TEST = (
    'import GBNF from "gbnf";\n\n'
    'describe("GBNF", () => {\n'
    '  it("returns the expected value", () => {\n'
    "    expect(GBNF()).toBe(42);\n"
    "  });\n"
    "});\n"
)

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


def write_python_suite(tests_directory: Path) -> None:
    """One unit test plus the grammar-fixtures test at the path the real suite uses."""
    directory = tests_directory / "python"
    (directory / "iteration").mkdir(parents=True)
    (directory / "gbnf_test.py").write_text(PYTHON_TEST)
    (directory / "iteration" / "grammars_test.py").write_text(PYTHON_TEST)


def write_typescript_suite(tests_directory: Path) -> None:
    directory = tests_directory / "typescript"
    (directory / "iteration").mkdir(parents=True)
    (directory / "gbnf.test.ts").write_text(TYPESCRIPT_TEST)
    (directory / "iteration" / "grammars.test.ts").write_text(TYPESCRIPT_TEST)


@pytest.fixture
def derivation_cache_key() -> str:
    return DERIVATION_CACHE_KEY


@pytest.fixture
def derivations_directory(tmp_path):
    directory = tmp_path / "derivations"
    tests_directory = directory / DERIVATION_CACHE_KEY / "tests"
    write_python_suite(tests_directory)
    write_typescript_suite(tests_directory)
    return directory


@pytest.fixture
def python_target(tmp_path):
    """A `gbnf/` package whose state supports `+` and whose error compares by value."""

    def build(value: int) -> Path:
        directory = tmp_path / f"python_target_{value}"
        (directory / "gbnf").mkdir(parents=True)
        (directory / "gbnf" / "__init__.py").write_text(PYTHON_PACKAGE_PORT.format(value=value))
        return directory

    return build


@pytest.fixture
def python_flat_target(tmp_path):
    """A flat `gbnf.py` with relative imports, an `add`-only state and a bare exception."""
    directory = tmp_path / "python_flat_target"
    directory.mkdir()
    (directory / "__init__.py").write_text(PYTHON_FLAT_INIT)
    (directory / "gbnf.py").write_text(PYTHON_FLAT_GBNF)
    (directory / "errors.py").write_text(PYTHON_FLAT_ERRORS)
    return directory


@pytest.fixture
def python_partial_target(python_target):
    """A passing port carrying a module the suite never imports."""
    directory = python_target(42)
    (directory / "unused.py").write_text(PYTHON_UNIMPORTED_MODULE)
    return directory


@pytest.fixture
def typescript_partial_target(tmp_path):
    """A passing port whose entry file exports a function the suite never calls."""
    directory = tmp_path / "typescript_partial_target"
    (directory / "src").mkdir(parents=True)
    (directory / "src" / "index.ts").write_text(TYPESCRIPT_UNCALLED_EXPORT)
    return directory


@pytest.fixture
def typescript_target(tmp_path):
    def build(value: int) -> Path:
        directory = tmp_path / f"typescript_target_{value}"
        (directory / "src").mkdir(parents=True)
        (directory / "src" / "index.ts").write_text(
            f"export default function GBNF(): number {{ return {value}; }}\n"
        )
        return directory

    return build


@pytest.fixture
def typescript_unresolvable_tsconfig_target(tmp_path):
    """A passing port whose tsconfig extends a file that is not on disk.

    The hand-written typescript reference is shaped this way: its tsconfig extends the
    monorepo root's, which the derivation cache does not carry.
    """
    directory = tmp_path / "typescript_unresolvable_tsconfig_target"
    (directory / "src").mkdir(parents=True)
    (directory / "src" / "index.ts").write_text(
        "export default function GBNF(): number { return 42; }\n"
    )
    (directory / "tsconfig.json").write_text(
        '{"extends": "../../../tsconfig.json", "compilerOptions": {"target": "esnext"}}\n'
    )
    return directory


@pytest.fixture
def typescript_named_target(tmp_path):
    """Exports `GBNF` by name only, with no default export."""
    directory = tmp_path / "typescript_named_target"
    (directory / "src").mkdir(parents=True)
    (directory / "src" / "index.ts").write_text(
        "export function GBNF(): number { return 42; }\n"
    )
    return directory


@pytest.fixture
def settings_derivations_directory(derivations_directory):
    """Redirects the CLI's derivation cache lookup at this fixture's synthetic cache.

    `settings.derivations_directory` is first-party and the CLI takes no parameter for
    it, so this is patched at its own binding rather than threaded through — the same
    carve-out gbnf-experiment's own tests/integration/conftest.py takes for the same field.
    """
    with patch.object(settings, "derivations_directory", derivations_directory):
        yield
