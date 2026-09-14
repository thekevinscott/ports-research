import { buildErrorPosition } from './buildErrorPosition.js';
import { codePointLength } from '../codePointLength.js';
import type { ValidInput } from './errorsTypes.js';
import { getInputAsString } from './getInputAsString.js';

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

  override toString(): string {
    return buildMessage(this.mostRecentInput, this.pos, this.previousInput);
  }

  equals(other: unknown): boolean {
    return other instanceof InputParseError && this.toString() === other.toString();
  }
}
