import type { ValidInput } from '../../grammar-graph/types.ts';
import { codePointLength } from '../code-points.ts';
import { buildErrorPosition } from './build-error-position.ts';
import { getInputAsString } from './get-input-as-string.ts';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  override name = 'InputParseError';
  private mostRecentInput: ValidInput;
  private pos: number;
  private previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    const previousAsString = getInputAsString(previousInput);
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        '',
        ...buildErrorPosition(
          `${previousAsString}${getInputAsString(mostRecentInput)}`,
          pos + codePointLength(previousAsString)
        ),
      ].join('\n')
    );
    Object.setPrototypeOf(this, InputParseError.prototype);
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
