import { buildErrorPosition } from './build-error-position.js';
import { getInputAsString, type ValidInput } from './get-input-as-string.js';
import { length } from '../js.js';

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
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        '',
        ...buildErrorPosition(
          `${previous}${getInputAsString(mostRecentInput)}`,
          pos + length(previous)
        ),
      ].join('\n')
    );
    Object.setPrototypeOf(this, InputParseError.prototype);
    this.name = 'InputParseError';
    this._mostRecentInput = mostRecentInput;
    this._pos = pos;
    this._previousInput = previousInput;
  }

  get mostRecentInput(): ValidInput {
    return this._mostRecentInput;
  }

  get pos(): number {
    return this._pos;
  }

  get previousInput(): ValidInput {
    return this._previousInput;
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
