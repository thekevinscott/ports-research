from __future__ import annotations

from typing import TYPE_CHECKING

from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

if TYPE_CHECKING:
    from ...grammar_graph.types import ValidInput

INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:'


class InputParseError(Exception):
    def __init__(self, most_recent_input: "ValidInput", pos: int, previous_input: "ValidInput" = ''):
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input
        super().__init__('\n'.join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            '',
            *build_error_position(
                f'{get_input_as_string(previous_input)}{get_input_as_string(most_recent_input)}',
                pos + len(get_input_as_string(previous_input)),
            ),
        ]))
        self.name = 'InputParseError'

    @property
    def message(self) -> str:
        return str(self)

    @property
    def src(self) -> str:
        return f'{get_input_as_string(self._previous_input)}{get_input_as_string(self._most_recent_input)}'

    @property
    def error_for_most_recent_input(self) -> str:
        return '\n'.join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            '',
            *build_error_position(get_input_as_string(self._most_recent_input), self._pos),
        ])

    # JS-name alias for parity with the reference implementation.
    @property
    def errorForMostRecentInput(self) -> str:
        return self.error_for_most_recent_input
