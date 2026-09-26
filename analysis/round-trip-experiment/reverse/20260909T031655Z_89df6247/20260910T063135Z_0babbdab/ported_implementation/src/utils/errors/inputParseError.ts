import { buildErrorPosition } from './buildErrorPosition.js';
import { getInputAsString, type InputSource } from './getInputAsString.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  public readonly name = 'InputParseError';
  private readonly mostRecentInput: InputSource;
  private readonly pos: number;
  private readonly previousInput: InputSource;

  public constructor(
    mostRecentInput: InputSource,
    pos: number,
    previousInput: InputSource = ''
  ) {
    const previous = getInputAsString(previousInput);
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        '',
        ...buildErrorPosition(
          `${previous}${getInputAsString(mostRecentInput)}`,
          pos + previous.length
        ),
      ].join('\n')
    );
    Object.setPrototypeOf(this, InputParseError.prototype);
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
  }

  public get src(): string {
    return `${getInputAsString(this.previousInput)}${getInputAsString(
      this.mostRecentInput
    )}`;
  }

  public get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this.mostRecentInput), this.pos),
    ].join('\n');
  }
}
