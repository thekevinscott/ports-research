import { buildErrorPosition } from './build-error-position.js';
import { ValidInput, getInputAsString } from './get-input-as-string.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  private _mostRecentInput: ValidInput;
  private _pos: number;
  private _previousInput: ValidInput;

  constructor(
    mostRecentInput: ValidInput,
    pos: number,
    previousInput: ValidInput = ''
  ) {
    const previous = getInputAsString(previousInput);
    const message = [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(
        `${previous}${getInputAsString(mostRecentInput)}`,
        pos + previous.length
      ),
    ].join('\n');
    super(message);
    this.name = 'InputParseError';
    this._mostRecentInput = mostRecentInput;
    this._pos = pos;
    this._previousInput = previousInput;
    Object.setPrototypeOf(this, InputParseError.prototype);
  }

  get src(): string {
    return `${getInputAsString(this._previousInput)}${getInputAsString(
      this._mostRecentInput
    )}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this._mostRecentInput), this._pos),
    ].join('\n');
  }
}
