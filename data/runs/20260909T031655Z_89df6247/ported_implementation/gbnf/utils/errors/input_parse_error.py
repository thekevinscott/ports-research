from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    name = "InputParseError"

    def __init__(self, most_recent_input, pos: int, previous_input=""):
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input
        previous = get_input_as_string(previous_input)
        message = "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    f"{previous}{get_input_as_string(most_recent_input)}",
                    pos + len(previous),
                ),
            ]
        )
        super().__init__(message)
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

    def _key(self):
        return (
            get_input_as_string(self._most_recent_input),
            self._pos,
            get_input_as_string(self._previous_input),
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, InputParseError):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())
