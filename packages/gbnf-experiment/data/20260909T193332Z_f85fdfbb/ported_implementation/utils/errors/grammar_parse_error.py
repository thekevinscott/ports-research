from __future__ import annotations

from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    """Raised when a grammar cannot be parsed."""

    def __init__(self, grammar: str, pos: int, reason: str):
        message = "\n".join([
            GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
            "",
            *build_error_position(grammar, pos),
        ])
        super().__init__(message)
        self.message = message
        self.name = "GrammarParseError"
        self.grammar = grammar
        self.reason = reason
        self.pos = pos

    def __str__(self) -> str:
        return self.message
