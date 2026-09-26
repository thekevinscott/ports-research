import { buildErrorPosition } from './buildErrorPosition.ts';
import type { ValidInput } from './errorsTypes.ts';
import { getInputAsString } from './getInputAsString.ts';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

const buildMessage = (mostRecentInput: ValidInput, pos: number, previousInput: ValidInput): string =>
  [
    INPUT_PARSER_ERROR_HEADER_MESSAGE,
    '',
    ...buildErrorPosition(
      `${getInputAsString(previousInput)}${getInputAsString(mostRecentInput)}`,
      pos + getInputAsString(previousInput).length,
    ),
  ].join('\n');

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
}
