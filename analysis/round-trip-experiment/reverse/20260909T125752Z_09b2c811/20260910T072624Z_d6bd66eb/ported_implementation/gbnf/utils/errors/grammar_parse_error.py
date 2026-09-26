"""Raised when a grammar cannot be parsed."""

from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str):
        message = "\n".join(
            [
                GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
                "",
                *build_error_position(grammar, pos),
            ]
        )
        super().__init__(message)
        self.message = message
        self.grammar = grammar
        self.pos = pos
        self.reason = reason

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        return type(other) is type(self) and str(other) == str(self)

    __hash__ = object.__hash__
