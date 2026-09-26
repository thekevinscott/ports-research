"""A library for parsing GBNF grammars."""

from .GBNF import GBNF

# grammar graph
from .grammar_graph.colorize import Color, colorize
from .grammar_graph.get_input_as_code_points import (
    get_code_point,
    get_input_as_code_points,
)
from .grammar_graph.get_parent_stack_id import get_parent_stack_id
from .grammar_graph.get_serialized_rule_key import (
    KEY_TRANSLATION,
    get_serialized_rule_key,
)
from .grammar_graph.grammar_graph_types import (
    PrintOpts,
    Range,
    ResolvedGraphPointer,
    ResolvedRule,
    Rule,
    RuleChar,
    RuleCharExclude,
    RuleCharValue,
    RuleEnd,
    RuleWithListOfIntsOrRanges,
    RuleWithValue,
    UnresolvedRule,
    ValidInput,
)
from .grammar_graph.graph import Graph, RootNode
from .grammar_graph.graph_node import GraphNode, GraphNodeMeta
from .grammar_graph.graph_pointer import GraphPointer
from .grammar_graph.parse_state import ParseState
from .grammar_graph.pointers import Pointers
from .grammar_graph.print import get_char, print_graph_node, print_graph_pointer
from .grammar_graph.rule_ref import RuleRef
from .grammar_graph.type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_range,
    is_rule,
    is_rule_char,
    is_rule_char_exclude,
    is_rule_end,
    is_rule_ref,
)

# grammar parser
from .grammar_parser.build_rule_stack import build_rule_stack, make_char_rule

# rules builder
from .rules_builder.is_word_char import is_word_char
from .rules_builder.parse_char import parse_char
from .rules_builder.parse_name import (
    PARSE_NAME_ERROR,
    VALID_NAME_SEPARATORS,
    parse_name,
)
from .rules_builder.parse_space import parse_space
from .rules_builder.rules_builder import RulesBuilder, get_out_elements
from .rules_builder.rules_builder_types import (
    InternalRuleDef,
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
    is_rule_def_alt,
    is_rule_def_char,
    is_rule_def_char_alt,
    is_rule_def_char_not,
    is_rule_def_char_rng_upper,
    is_rule_def_end,
    is_rule_def_ref,
)
from .rules_builder.symbol_ids import SymbolIds

# errors
from .utils.errors.build_error_position import (
    MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW,
    build_error_position,
)
from .utils.errors.get_input_as_string import get_input_as_string
from .utils.errors.grammar_parse_error import (
    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
    GrammarParseError,
)
from .utils.errors.input_parse_error import (
    INPUT_PARSER_ERROR_HEADER_MESSAGE,
    InputParseError,
)

# utils
from .utils.is_point_in_range import is_point_in_range
from .utils.validate_non_empty import validate_non_empty

__all__ = [
    "GBNF",
    "GRAMMAR_PARSER_ERROR_HEADER_MESSAGE",
    "INPUT_PARSER_ERROR_HEADER_MESSAGE",
    "KEY_TRANSLATION",
    "MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW",
    "PARSE_NAME_ERROR",
    "VALID_NAME_SEPARATORS",
    "Color",
    "Graph",
    "GraphNode",
    "GraphNodeMeta",
    "GraphPointer",
    "GrammarParseError",
    "InputParseError",
    "InternalRuleDef",
    "InternalRuleDefAlt",
    "InternalRuleDefChar",
    "InternalRuleDefCharAlt",
    "InternalRuleDefCharNot",
    "InternalRuleDefCharRngUpper",
    "InternalRuleDefEnd",
    "InternalRuleDefReference",
    "ParseState",
    "Pointers",
    "PrintOpts",
    "Range",
    "ResolvedGraphPointer",
    "ResolvedRule",
    "RootNode",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleCharValue",
    "RuleEnd",
    "RuleRef",
    "RuleWithListOfIntsOrRanges",
    "RuleWithValue",
    "RulesBuilder",
    "SymbolIds",
    "UnresolvedRule",
    "ValidInput",
    "build_error_position",
    "build_rule_stack",
    "colorize",
    "get_char",
    "get_code_point",
    "get_input_as_code_points",
    "get_input_as_string",
    "get_out_elements",
    "get_parent_stack_id",
    "get_serialized_rule_key",
    "is_graph_pointer_rule_char",
    "is_graph_pointer_rule_char_exclude",
    "is_graph_pointer_rule_end",
    "is_graph_pointer_rule_ref",
    "is_point_in_range",
    "is_range",
    "is_rule",
    "is_rule_char",
    "is_rule_char_exclude",
    "is_rule_def_alt",
    "is_rule_def_char",
    "is_rule_def_char_alt",
    "is_rule_def_char_not",
    "is_rule_def_char_rng_upper",
    "is_rule_def_end",
    "is_rule_def_ref",
    "is_rule_end",
    "is_rule_ref",
    "is_word_char",
    "make_char_rule",
    "parse_char",
    "parse_name",
    "parse_space",
    "print_graph_node",
    "print_graph_pointer",
    "validate_non_empty",
]
