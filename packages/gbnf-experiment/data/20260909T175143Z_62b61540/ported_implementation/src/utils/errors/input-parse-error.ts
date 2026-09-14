import { buildErrorPosition } from './build-error-position';
import { ValidInput } from './errors-types';
import { getInputAsString } from './get-input-as-string';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

const buildMessage = (src: string, pos: number): string => [
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
  '',
  ...buildErrorPosition(src, pos),
].join('\n');

export class InputParseError extends Error {
  mostRecentInput: ValidInput;
  pos: number;
  previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    super(buildMessage(
      `${getInputAsString(previousInput)}${getInputAsString(mostRecentInput)}`,
      pos + getInputAsString(previousInput).length,
    ));
    Object.setPrototypeOf(this, InputParseError.prototype);
    this.name = 'InputParseError';
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
  }

  get src(): string {
    return `${getInputAsString(this.previousInput)}${getInputAsString(this.mostRecentInput)}`;
  }

  get errorForMostRecentInput(): string {
    return buildMessage(getInputAsString(this.mostRecentInput), this.pos);
  }
}
