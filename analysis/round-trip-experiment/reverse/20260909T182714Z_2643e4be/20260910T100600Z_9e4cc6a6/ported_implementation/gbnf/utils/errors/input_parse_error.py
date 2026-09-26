from __future__ import annotations

from .build_error_position import build_error_position
from .errors_types import ValidInput
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: ValidInput,
        pos: int,
        previous_input: ValidInput = "",
    ) -> None:
        self.most_recent_input = most_recent_input
        self.pos = pos
        self.previous_input = previous_input
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        previous_input = get_input_as_string(self.previous_input)
        return "\n".join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                "",
                *build_error_position(
                    f"{previous_input}{get_input_as_string(self.most_recent_input)}",
                    self.pos + len(previous_input),
                ),
            ],
        )

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
                    get_input_as_string(self.most_recent_input),
                    self.pos,
                ),
            ],
        )

    def __str__(self) -> str:
        return self._build_message()

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)
