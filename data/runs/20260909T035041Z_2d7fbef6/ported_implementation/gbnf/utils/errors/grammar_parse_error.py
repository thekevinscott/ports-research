from __future__ import annotations

from ..js import join
from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str):
        super().__init__(
            join(
                [
                    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
                    "",
                    *build_error_position(grammar, pos),
                ],
                "\n",
            )
        )
        self.name = "GrammarParseError"
        self.grammar = grammar
        self.reason = reason
        self.pos = pos

    @property
    def message(self) -> str:
        return str(self)
