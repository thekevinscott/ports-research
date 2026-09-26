import json
import sys
import types
from pathlib import Path

import pytest

import execute_test_suite.adapt_python as adapt_python
from execute_test_suite.adapt_python import (
    REPORT_VARIABLE,
    RULES,
    TARGET_VARIABLE,
    exception_eq,
    flat_module,
    pytest_configure,
    pytest_sessionfinish,
    state_add,
)

FLAT_INIT = "from .gbnf import GBNF, InputParseError\n"
FLAT_GBNF = (
    "from .errors import InputParseError\n\n\n"
    "class State:\n"
    "    def add(self, text):\n"
    "        return State()\n\n\n"
    "def GBNF(grammar, initial=''):\n"
    "    return State()\n"
)
FLAT_ERRORS = "class InputParseError(Exception):\n    pass\n"


@pytest.fixture
def fired(monkeypatch):
    fired = set()
    monkeypatch.setattr(adapt_python, "fired", fired)
    return fired


@pytest.fixture
def forget_gbnf():
    yield
    for name in [n for n in sys.modules if n == "gbnf" or n.startswith("gbnf.")]:
        del sys.modules[name]


@pytest.fixture
def flat_target(tmp_path):
    target = tmp_path / "flat"
    target.mkdir()
    (target / "__init__.py").write_text(FLAT_INIT)
    (target / "gbnf.py").write_text(FLAT_GBNF)
    (target / "errors.py").write_text(FLAT_ERRORS)
    return target


@pytest.fixture
def package_target(tmp_path):
    target = tmp_path / "package"
    (target / "gbnf").mkdir(parents=True)
    (target / "gbnf" / "__init__.py").write_text(FLAT_GBNF)
    (target / "gbnf" / "errors.py").write_text(FLAT_ERRORS)
    return target


class Addable:
    def add(self, text):
        return ("add", text)

    def __add__(self, text):
        return ("dunder", text)


class Plain:
    pass


def module_with(**names):
    module = types.ModuleType("gbnf")
    module.__dict__.update(names)
    return module


def describe_rules():
    def it_names_the_three_python_rules_in_report_order():
        assert RULES == ("flat_module", "state_add", "exception_eq")


def describe_flat_module():
    def it_does_not_fire_for_a_gbnf_package(package_target):
        assert flat_module(package_target) is False
        assert "gbnf" not in sys.modules

    def it_does_not_fire_when_there_is_no_gbnf_py(tmp_path):
        assert flat_module(tmp_path) is False

    def it_loads_the_port_root_as_the_gbnf_package(flat_target, forget_gbnf):
        assert flat_module(flat_target) is True
        gbnf = sys.modules["gbnf"]
        assert callable(gbnf.GBNF)
        assert issubclass(gbnf.InputParseError, Exception)

    def it_resolves_the_flat_modules_relative_imports(flat_target, forget_gbnf):
        flat_module(flat_target)
        assert sys.modules["gbnf.errors"].InputParseError is sys.modules["gbnf"].InputParseError


def describe_state_add():
    def it_wraps_gbnf_so_the_returned_state_gains_add_as_its_plus(fired):
        class AddOnly:
            def add(self, text):
                return ("add", text)

        module = module_with(GBNF=lambda grammar, initial="": AddOnly())
        state_add(module)
        state = module.GBNF("root ::= 'a'")
        assert state + "a" == ("add", "a")
        assert fired == {"state_add"}

    def it_leaves_a_state_that_already_has_a_plus_alone(fired):
        module = module_with(GBNF=lambda grammar: Addable())
        state_add(module)
        assert module.GBNF("root") + "a" == ("dunder", "a")
        assert fired == set()

    def it_leaves_a_state_without_add_alone(fired):
        module = module_with(GBNF=lambda grammar: Plain())
        state_add(module)
        module.GBNF("root")
        assert not hasattr(Plain, "__add__")
        assert fired == set()

    def it_forwards_every_argument_to_the_port(fired):
        calls = []

        def GBNF(*args, **kwargs):
            calls.append((args, kwargs))
            return Plain()

        module = module_with(GBNF=GBNF)
        state_add(module)
        module.GBNF("root", "abc", strict=True)
        assert calls == [(("root", "abc"), {"strict": True})]

    def it_does_nothing_when_the_module_has_no_gbnf(fired):
        module = module_with()
        state_add(module)
        assert not hasattr(module, "GBNF")


def describe_exception_eq():
    def it_gives_exceptions_without_their_own_eq_a_type_and_args_equality():
        class E(Exception):
            pass

        assert exception_eq(module_with(E=E)) is True
        assert E("a", 1) == E("a", 1)
        assert E("a", 1) != E("a", 2)
        assert hash(E("a", 1)) == hash(E("a", 1))

    def it_distinguishes_sibling_exception_types_with_the_same_args():
        class A(Exception):
            pass

        class B(Exception):
            pass

        exception_eq(module_with(A=A, B=B))
        assert A("x") != B("x")

    def it_leaves_an_exception_with_its_own_eq_alone():
        class E(Exception):
            def __eq__(self, other):
                return True

        assert exception_eq(module_with(E=E)) is False
        assert E("a") == E("b")

    def it_ignores_names_that_are_not_exception_classes():
        assert exception_eq(module_with(Plain=Plain, value=3)) is False


def describe_pytest_configure():
    def it_runs_every_rule_against_the_port_named_in_the_environment(
        flat_target, fired, forget_gbnf, monkeypatch
    ):
        monkeypatch.setenv(TARGET_VARIABLE, str(flat_target))
        pytest_configure(None)
        gbnf = sys.modules["gbnf"]
        state = gbnf.GBNF("root")
        assert isinstance(state + "a", type(state))
        assert gbnf.InputParseError("a") == gbnf.InputParseError("a")
        assert fired == {"flat_module", "state_add", "exception_eq"}

    def it_imports_a_gbnf_package_from_the_path(package_target, fired, forget_gbnf, monkeypatch):
        monkeypatch.setenv(TARGET_VARIABLE, str(package_target))
        monkeypatch.syspath_prepend(str(package_target))
        pytest_configure(None)
        assert "flat_module" not in fired
        assert fired == {"exception_eq"}

    def it_leaves_the_suite_to_fail_as_it_would_when_gbnf_cannot_be_imported(
        tmp_path, fired, forget_gbnf, monkeypatch
    ):
        monkeypatch.setenv(TARGET_VARIABLE, str(tmp_path))
        pytest_configure(None)
        assert fired == set()


def describe_pytest_sessionfinish():
    def it_writes_the_fired_rules_in_report_order(tmp_path, fired, monkeypatch):
        report = tmp_path / "adapt.json"
        monkeypatch.setenv(REPORT_VARIABLE, str(report))
        fired.update({"exception_eq", "flat_module"})
        pytest_sessionfinish(None)
        assert json.loads(report.read_text()) == {"rules_fired": ["flat_module", "exception_eq"]}

    def it_writes_an_empty_list_when_nothing_fired(tmp_path, fired, monkeypatch):
        report = tmp_path / "adapt.json"
        monkeypatch.setenv(REPORT_VARIABLE, str(report))
        pytest_sessionfinish(None)
        assert json.loads(report.read_text()) == {"rules_fired": []}
