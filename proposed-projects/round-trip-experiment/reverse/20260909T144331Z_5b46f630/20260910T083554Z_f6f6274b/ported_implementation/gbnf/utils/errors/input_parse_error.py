from ..code_point_length import code_point_length
from .build_error_position import build_error_position
from .errors_types import ValidInput
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


def _build_message(
    most_recent_input: ValidInput, pos: int, previous_input: ValidInput
) -> str:
    previous = get_input_as_string(previous_input)
    return "\n".join(
        [
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            *build_error_position(
                f"{previous}{get_input_as_string(most_recent_input)}",
                pos + code_point_length(previous),
            ),
        ]
    )


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: ValidInput,
        pos: int,
        previous_input: ValidInput = "",
    ):
        super().__init__(_build_message(most_recent_input, pos, previous_input))
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
        return "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    get_input_as_string(self.most_recent_input), self.pos
                ),
            ]
        )

    def __str__(self) -> str:
        return _build_message(self.most_recent_input, self.pos, self.previous_input)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, InputParseError) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))
