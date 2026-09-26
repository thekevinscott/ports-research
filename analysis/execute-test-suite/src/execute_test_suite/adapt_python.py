"""pytest plugin that adapts a python port's surface to the reference `gbnf` API.

Copied whole into the runner's scratch directory and loaded with `-p`, so it runs
inside the graded interpreter and must stay stdlib-only. The rule list below is
the whole python policy; `fired` collects the names that applied this session.
"""

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path

RULES = ("flat_module", "state_add", "exception_eq")
TARGET_VARIABLE = "EXECUTE_TEST_SUITE_ADAPT_TARGET"
REPORT_VARIABLE = "EXECUTE_TEST_SUITE_ADAPT_REPORT"

fired: set[str] = set()


def flat_module(target: Path) -> bool:
    """A flat `gbnf.py` at the port root, loaded as the `gbnf` package.

    With the port root on `sys.path`, `import gbnf` finds the flat file and its
    relative imports have no parent package. Registering the root itself as the
    package gives them one.
    """
    if not (target / "gbnf.py").is_file() or (target / "gbnf").is_dir():
        return False
    spec = importlib.util.spec_from_file_location(
        "gbnf", target / "__init__.py", submodule_search_locations=[str(target)]
    )
    package = importlib.util.module_from_spec(spec)
    sys.modules["gbnf"] = package
    spec.loader.exec_module(package)
    return True


def state_add(module) -> None:
    """Wrap `GBNF` so the state it returns accepts `state + text` via `state.add`."""
    port_gbnf = getattr(module, "GBNF", None)
    if port_gbnf is None:
        return

    def GBNF(*args, **kwargs):
        state = port_gbnf(*args, **kwargs)
        cls = type(state)
        if not hasattr(cls, "__add__") and callable(getattr(cls, "add", None)):
            cls.__add__ = lambda self, text: self.add(text)
            fired.add("state_add")
        return state

    module.GBNF = GBNF


def exception_eq(module) -> bool:
    """Give exported exception classes that inherit `object.__eq__` value equality."""
    patched = False
    for value in list(vars(module).values()):
        if (
            isinstance(value, type)
            and issubclass(value, BaseException)
            and value.__eq__ is object.__eq__
        ):
            value.__eq__ = lambda self, other: (
                type(self) is type(other) and self.args == other.args
            )
            value.__hash__ = lambda self: hash((type(self), self.args))
            patched = True
    return patched


def pytest_configure(config) -> None:
    target = Path(os.environ[TARGET_VARIABLE])
    try:
        if flat_module(target):
            fired.add("flat_module")
        module = importlib.import_module("gbnf")
    except Exception:
        return
    state_add(module)
    if exception_eq(module):
        fired.add("exception_eq")


def pytest_sessionfinish(session) -> None:
    Path(os.environ[REPORT_VARIABLE]).write_text(
        json.dumps({"rules_fired": [rule for rule in RULES if rule in fired]})
    )
