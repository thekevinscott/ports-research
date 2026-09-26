from __future__ import annotations

from .build_error_position import build_error_position
from .get_input_as_string import get_input_as_string
from .types import ValidInput

INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:'


class InputParseError(Exception):
    def __init__(
        self,
        most_recent_input: ValidInput,
        pos: int,
        previous_input: ValidInput = '',
    ):
        previous = get_input_as_string(previous_input)
        super().__init__(
            '\n'.join(
                [
                    INPUT_PARSER_ERROR_HEADER_MESSAGE,
                    '',
                    *build_error_position(
                        f'{previous}{get_input_as_string(most_recent_input)}',
                        pos + len(previous),
                    ),
                ]
            )
        )
        self.name = 'InputParseError'
        self.most_recent_input = most_recent_input
        self.pos = pos
        self.previous_input = previous_input

    @property
    def src(self) -> str:
        return (
            f'{get_input_as_string(self.previous_input)}'
            f'{get_input_as_string(self.most_recent_input)}'
        )

    @property
    def error_for_most_recent_input(self) -> str:
        return '\n'.join(
            [
                INPUT_PARSER_ERROR_HEADER_MESSAGE,
                '',
                *build_error_position(
                    get_input_as_string(self.most_recent_input), self.pos
                ),
            ]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InputParseError):
            return NotImplemented
        # The most recent input may be held as a string or as code points; compare
        # the rendered form so the two representations line up.
        return (
            self.pos == other.pos
            and self.src == other.src
            and str(self) == str(other)
        )

    def __hash__(self) -> int:
        return hash((self.pos, self.src))
