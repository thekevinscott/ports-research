import type { ValidInput } from '../../grammar-graph/types.js';
import { buildErrorPosition } from './build-error-position.js';
import { getInputAsString } from './get-input-as-string.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE =
  'Failed to parse input string:';

export class InputParseError extends Error {
  private mostRecentInput: ValidInput;
  private pos: number;
  private previousInput: ValidInput;

  constructor(
    mostRecentInput: ValidInput,
    pos: number,
    previousInput: ValidInput = '',
  ) {
    const previousAsString = getInputAsString(previousInput);
    const message = [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(
        `${previousAsString}${getInputAsString(mostRecentInput)}`,
        pos + previousAsString.length,
      ),
    ].join('\n');
    super(message);
    this.name = 'InputParseError';
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
    Object.setPrototypeOf(this, InputParseError.prototype);
  }

  get src(): string {
    return `${getInputAsString(this.previousInput)}${getInputAsString(
      this.mostRecentInput,
    )}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this.mostRecentInput), this.pos),
    ].join('\n');
  }
}
