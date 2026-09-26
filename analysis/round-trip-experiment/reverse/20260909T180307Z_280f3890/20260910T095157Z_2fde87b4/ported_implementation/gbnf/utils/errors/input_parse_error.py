from .build_error_position import build_error_position
from .errors_types import ValidInput
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


def _build_message(src: str, pos: int) -> str:
    return "\n".join(
        [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", *build_error_position(src, pos)]
    )


class InputParseError(Exception):
    def __init__(
        self, most_recent_input: ValidInput, pos: int, previous_input: ValidInput = ""
    ):
        previous = get_input_as_string(previous_input)
        message = _build_message(
            f"{previous}{get_input_as_string(most_recent_input)}", pos + len(previous)
        )
        super().__init__(message)
        self.name = "InputParseError"
        self.message = message
        self.most_recent_input = most_recent_input
        self.pos = pos
        self.previous_input = previous_input

    @property
    def src(self) -> str:
        return (
            f"{get_input_as_string(self.previous_input)}"
            f"{get_input_as_string(self.most_recent_input)}"
        )

    @property
    def error_for_most_recent_input(self) -> str:
        return _build_message(get_input_as_string(self.most_recent_input), self.pos)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InputParseError):
            return NotImplemented
        return str(self) == str(other)

    __hash__ = object.__hash__
