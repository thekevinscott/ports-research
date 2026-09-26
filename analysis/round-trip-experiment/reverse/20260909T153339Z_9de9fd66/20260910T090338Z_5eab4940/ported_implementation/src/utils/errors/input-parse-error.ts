import { buildErrorPosition } from './build-error-position.js';
import { getInputAsString, type ValidInput } from './get-input-as-string.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  override name = 'InputParseError';

  // inputs are normalized to strings up front, so that an error built from code
  // points reads the same as one built from the equivalent string.
  private mostRecentInput: string;
  private previousInput: string;
  private pos: number;

  constructor(
    mostRecentInput: ValidInput,
    pos: number,
    previousInput: ValidInput = ''
  ) {
    const mostRecent = getInputAsString(mostRecentInput);
    const previous = getInputAsString(previousInput);
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        '',
        ...buildErrorPosition(`${previous}${mostRecent}`, pos + previous.length),
      ].join('\n')
    );
    this.mostRecentInput = mostRecent;
    this.previousInput = previous;
    this.pos = pos;
  }

  get src(): string {
    return `${this.previousInput}${this.mostRecentInput}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(this.mostRecentInput, this.pos),
    ].join('\n');
  }
}
