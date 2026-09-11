import { codePointLength } from '../code-point-length.ts';
import { buildErrorPosition } from './build-error-position.ts';
import type { ValidInput } from './errors-types.ts';
import { getInputAsString } from './get-input-as-string.ts';

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
        pos + codePointLength(getInputAsString(previousInput)),
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
      ...buildErrorPosition(
        getInputAsString(this.mostRecentInput),
        this.pos,
      ),
    ].join('\n');
  }

  toString(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(
        `${getInputAsString(this.previousInput)}${getInputAsString(this.mostRecentInput)}`,
        this.pos + codePointLength(getInputAsString(this.previousInput)),
      ),
    ].join('\n');
  }

  equals(other: unknown): boolean {
    return String(this) === String(other);
  }
}
