#!/usr/bin/env python3
"""Run the port's test suite: `python3 ported_implementation/run_tests.py`.

Equivalent to `python3 -m pytest ported_implementation/tests` where pytest is
available; the tests themselves are plain `unittest`, so neither is required.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def main() -> int:
    sys.path.insert(0, str(HERE.parent))
    sys.path.insert(0, str(HERE / "tests"))
    suite = unittest.TestLoader().discover(str(HERE / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
