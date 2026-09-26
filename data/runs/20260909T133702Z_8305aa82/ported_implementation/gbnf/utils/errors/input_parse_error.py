from ...grammar_graph.types import ValidInput
from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: ValidInput,
        pos: int,
        previous_input: ValidInput = "",
    ):
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input
        previous_as_string = get_input_as_string(previous_input)
        message = "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    f"{previous_as_string}{get_input_as_string(most_recent_input)}",
                    pos + len(previous_as_string),
                ),
            ]
        )
        super().__init__(message)
        self.name = "InputParseError"
        self.message = message

    def __str__(self) -> str:
        return self.message

    @property
    def src(self) -> str:
        return (
            f"{get_input_as_string(self._previous_input)}"
            f"{get_input_as_string(self._most_recent_input)}"
        )

    @property
    def error_for_most_recent_input(self) -> str:
        return "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    get_input_as_string(self._most_recent_input), self._pos
                ),
            ]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InputParseError):
            return NotImplemented
        return self.message == other.message and self.src == other.src

    def __hash__(self) -> int:
        return hash(self.message)
