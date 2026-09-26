"""Python port of the TypeScript `gbnf` reference implementation.

The library itself lives in the :mod:`gbnf` package alongside this file. This module
re-exports its public API so the port can be used either way::

    from ported_implementation import GBNF        # with /workspace on sys.path
    from gbnf import GBNF                         # with ported_implementation on sys.path
"""

from .gbnf import (
    GBNF,
    GrammarParseError,
    InputParseError,
    ParseState,
    Range,
    Rule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    ValidInput,
    is_range,
)

__all__ = [
    "GBNF",
    "is_range",
    "RuleType",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "Range",
    "ValidInput",
    "ParseState",
    "InputParseError",
    "GrammarParseError",
]
