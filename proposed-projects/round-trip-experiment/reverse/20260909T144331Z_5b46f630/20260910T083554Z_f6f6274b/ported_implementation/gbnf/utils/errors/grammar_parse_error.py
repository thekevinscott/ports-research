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
        super().__init__(_build_message(grammar, pos, reason))
        self.grammar = grammar
        self.pos = pos
        self.reason = reason

    def __str__(self) -> str:
        return _build_message(self.grammar, self.pos, self.reason)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GrammarParseError) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))
