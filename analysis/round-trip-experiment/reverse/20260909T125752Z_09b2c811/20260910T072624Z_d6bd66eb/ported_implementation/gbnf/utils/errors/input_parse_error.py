"""Raised when an input cannot be parsed by a grammar."""

from .build_error_position import build_error_position
from .get_input_as_string import ValidInput, get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: ValidInput,
        pos: int,
        previous_input: ValidInput = "",
    ):
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
        self.message = message
        self.most_recent_input = most_recent_input
        self.pos = pos
        self.previous_input = previous_input

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        return type(other) is type(self) and str(other) == str(self)

    __hash__ = object.__hash__

    @property
    def src(self) -> str:
        return (
            f"{get_input_as_string(self.previous_input)}"
            f"{get_input_as_string(self.most_recent_input)}"
        )

    @property
    def error_for_most_recent_input(self) -> str:
        return "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    get_input_as_string(self.most_recent_input), self.pos
                ),
            ]
        )
