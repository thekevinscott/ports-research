"""Port of ``src/utils/errors/input-parse-error.ts``."""
from __future__ import annotations

from ...valid_input import ValidInput
from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string

INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:'


class InputParseError(Exception):
    def __init__(self, most_recent_input: ValidInput, pos: int, previous_input: ValidInput = ''):
        self._most_recent_input = most_recent_input
        self._pos = pos
        self._previous_input = previous_input
        previous = get_input_as_string(previous_input)
        message = '\n'.join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            '',
            *build_error_position(
                f'{previous}{get_input_as_string(most_recent_input)}',
                pos + len(previous),
            ),
        ])
        super().__init__(message)
        self.name = 'InputParseError'
        self.message = message

    @property
    def src(self) -> str:
        return (
            f'{get_input_as_string(self._previous_input)}'
            f'{get_input_as_string(self._most_recent_input)}'
        )

    @property
    def error_for_most_recent_input(self) -> str:
        return '\n'.join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            '',
            *build_error_position(get_input_as_string(self._most_recent_input), self._pos),
        ])
