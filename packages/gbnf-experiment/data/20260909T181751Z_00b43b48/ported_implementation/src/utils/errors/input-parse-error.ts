import { buildErrorPosition } from './build-error-position.js';
import type { ValidInput } from './errors-types.js';
import { getInputAsString } from './get-input-as-string.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  mostRecentInput: ValidInput;
  pos: number;
  previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    super([
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(
        `${getInputAsString(previousInput)}${getInputAsString(mostRecentInput)}`,
        pos + getInputAsString(previousInput).length,
      ),
    ].join('\n'));
    this.name = 'InputParseError';
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
    Object.setPrototypeOf(this, InputParseError.prototype);
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
