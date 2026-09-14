import sys as _sys

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range
from .grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd, RuleType
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

# resolving pointers through deeply nested grammars recurses once per nesting level,
# which outgrows CPython's default ceiling well before any real grammar does.
if _sys.getrecursionlimit() < 20000:
    _sys.setrecursionlimit(20000)

__all__ = [
    "GBNF",
    "ParseState",
    "RuleType",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "is_range",
    "GrammarParseError",
    "InputParseError",
]
