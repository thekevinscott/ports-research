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
        # inputs are normalized to strings up front so that an error built from code
        # points compares equal to the same error built from the equivalent string.
        self._most_recent_input = get_input_as_string(most_recent_input)
        self._previous_input = get_input_as_string(previous_input)
        self._pos = pos
        message = "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    f"{self._previous_input}{self._most_recent_input}",
                    pos + len(self._previous_input),
                ),
            ]
        )
        super().__init__(message)
        self.name = "InputParseError"
        self.message = message

    @property
    def src(self) -> str:
        return f"{self._previous_input}{self._most_recent_input}"

    @property
    def error_for_most_recent_input(self) -> str:
        return "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(self._most_recent_input, self._pos),
            ]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InputParseError):
            return NotImplemented
        return (self._most_recent_input, self._pos, self._previous_input) == (
            other._most_recent_input,
            other._pos,
            other._previous_input,
        )

    def __hash__(self) -> int:
        return hash((self._most_recent_input, self._pos, self._previous_input))
