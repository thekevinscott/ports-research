from __future__ import annotations

from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str) -> None:
        self.grammar = grammar
        self.pos = pos
        self.reason = reason
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        return "\n".join(
            [
                GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(self.reason),
                "",
                *build_error_position(self.grammar, self.pos),
            ],
        )

    def __str__(self) -> str:
        return self._build_message()

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)
