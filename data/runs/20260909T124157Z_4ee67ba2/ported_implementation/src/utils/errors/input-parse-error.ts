import { buildErrorPosition } from './build-error-position.ts';
import type { ValidInput } from './errors-types.ts';
import { getInputAsString } from './get-input-as-string.ts';

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
      pos + previous.length,
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

  toString(): string {
    return buildMessage(this.mostRecentInput, this.pos, this.previousInput);
  }

  equals(other: unknown): boolean {
    return String(this) === String(other);
  }
}
