from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str):
        super().__init__(
            "\n".join(
                [
                    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
                    "",
                    *build_error_position(grammar, pos),
                ]
            )
        )
        self.name = "GrammarParseError"
        self.grammar = grammar
        self.reason = reason
        self.pos = pos

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GrammarParseError):
            return NotImplemented
        return (self.grammar, self.pos, self.reason) == (
            other.grammar,
            other.pos,
            other.reason,
        )

    def __hash__(self) -> int:
        return hash((self.grammar, self.pos, self.reason))
