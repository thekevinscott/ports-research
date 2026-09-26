import { buildErrorPosition } from './build-error-position.ts';
import type { ValidInput } from './errors-types.ts';
import { getInputAsString } from './get-input-as-string.ts';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

const buildMessage = (src: string, pos: number): string =>
  [
    INPUT_PARSER_ERROR_HEADER_MESSAGE,
    '',
    ...buildErrorPosition(src, pos),
  ].join('\n');

export class InputParseError extends Error {
  mostRecentInput: ValidInput;
  pos: number;
  previousInput: ValidInput;

  constructor(
    mostRecentInput: ValidInput,
    pos: number,
    previousInput: ValidInput = ''
  ) {
    const previous = getInputAsString(previousInput);
    super(
      buildMessage(
        `${previous}${getInputAsString(mostRecentInput)}`,
        pos + previous.length
      )
    );
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
    return buildMessage(getInputAsString(this.mostRecentInput), this.pos);
  }
}
