from dataclasses import dataclass

import tree_sitter_python as tspython
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser


@dataclass
class LanguageSpec:
    parsers: dict[str, Parser]
    identifiers: frozenset[str]


PYTHON = LanguageSpec(
    parsers={".py": Parser(Language(tspython.language()))},
    identifiers=frozenset({"identifier"}),
)

TYPESCRIPT = LanguageSpec(
    parsers={
        ".ts": Parser(Language(tsts.language_typescript())),
        ".tsx": Parser(Language(tsts.language_tsx())),
    },
    identifiers=frozenset(
        {
            "identifier",
            "property_identifier",
            "type_identifier",
            "shorthand_property_identifier",
            "shorthand_property_identifier_pattern",
            "private_property_identifier",
            "statement_identifier",
        }
    ),
)

LANGUAGES = {"python": PYTHON, "typescript": TYPESCRIPT}
