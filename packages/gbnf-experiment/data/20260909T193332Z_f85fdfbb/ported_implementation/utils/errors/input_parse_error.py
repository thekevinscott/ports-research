from __future__ import annotations

from typing import TYPE_CHECKING

from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

if TYPE_CHECKING:  # pragma: no cover
    from ...grammar_graph.types import ValidInput

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    """Raised when an input string cannot be matched against the grammar."""

    def __init__(
        self,
        most_recent_input: "ValidInput",
        pos: int,
        previous_input: "ValidInput" = "",
    ):
        previous_as_string = get_input_as_string(previous_input)
        message = "\n".join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            *build_error_position(
                f"{previous_as_string}{get_input_as_string(most_recent_input)}",
                pos + len(previous_as_string),
            ),
        ])
        super().__init__(message)
        self.message = message
        self.name = "InputParseError"
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input

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
        return "\n".join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            *build_error_position(
                get_input_as_string(self._most_recent_input), self._pos
            ),
        ])

    # camelCase alias, mirroring the reference API.
    errorForMostRecentInput = error_for_most_recent_input
