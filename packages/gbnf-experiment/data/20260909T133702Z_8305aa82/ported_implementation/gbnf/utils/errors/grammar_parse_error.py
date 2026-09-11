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
        self.name = "GrammarParseError"
        self.message = message
        self.grammar = grammar
        self.reason = reason
        self.pos = pos

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GrammarParseError):
            return NotImplemented
        return (
            self.grammar == other.grammar
            and self.pos == other.pos
            and self.reason == other.reason
            and self.message == other.message
        )

    def __hash__(self) -> int:
        return hash((self.grammar, self.pos, self.reason))
