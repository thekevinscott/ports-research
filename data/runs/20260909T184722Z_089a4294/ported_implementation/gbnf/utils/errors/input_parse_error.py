from __future__ import annotations

from typing import TYPE_CHECKING

from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

if TYPE_CHECKING:
    from ...grammar_graph.types import ValidInput

INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:"


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: "ValidInput",
        pos: int,
        previous_input: "ValidInput" = "",
    ):
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input
        previous = get_input_as_string(previous_input)
        super().__init__(
            "\n".join(
                [
                    INPUT_PARSER_ERROR_HEADER_MESSAGE,
                    "",
                    *build_error_position(
                        f"{previous}{get_input_as_string(most_recent_input)}",
                        pos + len(previous),
                    ),
                ]
            )
        )
        self.name = "InputParseError"

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
        return type(self) is type(other) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash((type(self), str(self)))
