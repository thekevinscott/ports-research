from dataclasses import dataclass

import tree_sitter_python as tspython
import tree_sitter_typescript as tsts
from tree_sitter import Language, Node, Parser


@dataclass
class LanguageSpec:
    parsers: dict[str, Parser]
    functions: frozenset[str]
    branches: frozenset[str]
    branch_operators: dict[str, frozenset[str]]

    def is_branch(self, node: Node) -> bool:
        if node.type in self.branches:
            return True
        operators = self.branch_operators.get(node.type)
        if not operators:
            return False
        operator = node.child_by_field_name("operator")
        return operator is not None and operator.type in operators


PYTHON = LanguageSpec(
    parsers={".py": Parser(Language(tspython.language()))},
    functions=frozenset({"function_definition"}),
    branches=frozenset(
        {
            "if_statement",
            "elif_clause",
            "for_statement",
            "while_statement",
            "except_clause",
            "case_clause",
            "conditional_expression",
            "boolean_operator",
            "if_clause",
        }
    ),
    branch_operators={},
)

TYPESCRIPT = LanguageSpec(
    parsers={
        ".ts": Parser(Language(tsts.language_typescript())),
        ".tsx": Parser(Language(tsts.language_tsx())),
    },
    functions=frozenset(
        {
            "function_declaration",
            "method_definition",
            "arrow_function",
            "function_expression",
            "generator_function_declaration",
        }
    ),
    branches=frozenset(
        {
            "if_statement",
            "for_statement",
            "for_in_statement",
            "while_statement",
            "do_statement",
            "switch_case",
            "catch_clause",
            "ternary_expression",
        }
    ),
    branch_operators={"binary_expression": frozenset({"&&", "||", "??"})},
)

LANGUAGES = {"python": PYTHON, "typescript": TYPESCRIPT}
