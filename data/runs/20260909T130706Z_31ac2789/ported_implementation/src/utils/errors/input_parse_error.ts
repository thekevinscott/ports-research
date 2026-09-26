import { codePointLength } from '../code_point_length.ts';
import { buildErrorPosition } from './build_error_position.ts';
import type { ValidInput } from './errors_types.ts';
import { getInputAsString } from './get_input_as_string.ts';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

const buildMessage = (
  mostRecentInput: ValidInput,
  pos: number,
  previousInput: ValidInput,
): string => {
  const previous = getInputAsString(previousInput);
  return [
    INPUT_PARSER_ERROR_HEADER_MESSAGE,
    '',
    ...buildErrorPosition(
      `${previous}${getInputAsString(mostRecentInput)}`,
      pos + codePointLength(previous),
    ),
  ].join('\n');
};

export class InputParseError extends Error {
  mostRecentInput: ValidInput;
  pos: number;
  previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    super(buildMessage(mostRecentInput, pos, previousInput));
    this.name = 'InputParseError';
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
  }

  get src(): string {
    return `${getInputAsString(this.previousInput)}${getInputAsString(this.mostRecentInput)}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this.mostRecentInput), this.pos),
    ].join('\n');
  }

  get error_for_most_recent_input(): string {
    return this.errorForMostRecentInput;
  }

  get most_recent_input(): ValidInput {
    return this.mostRecentInput;
  }

  get previous_input(): ValidInput {
    return this.previousInput;
  }

  toString(): string {
    return buildMessage(this.mostRecentInput, this.pos, this.previousInput);
  }
}
