from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


def _build_message(grammar: str, pos: int, reason: str) -> str:
    return "\n".join(
        [
            GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
            "",
            *build_error_position(grammar, pos),
        ]
    )


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str):
        message = _build_message(grammar, pos, reason)
        super().__init__(message)
        self.name = "GrammarParseError"
        self.message = message
        self.grammar = grammar
        self.pos = pos
        self.reason = reason

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GrammarParseError):
            return NotImplemented
        return str(self) == str(other)

    __hash__ = object.__hash__
