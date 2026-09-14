from .build_error_position import build_error_position


def GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason: str) -> str:
    return f"Failed to parse grammar: {reason}"


class GrammarParseError(Exception):
    def __init__(self, grammar: str, pos: int, reason: str) -> None:
        super().__init__(
            "\n".join(
                [
                    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
                    "",
                    *build_error_position(grammar, pos),
                ]
            )
        )
        self.grammar = grammar
        self.pos = pos
        self.reason = reason

    def __str__(self) -> str:
        return "\n".join(
            [
                GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(self.reason),
                "",
                *build_error_position(self.grammar, self.pos),
            ]
        )

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))
