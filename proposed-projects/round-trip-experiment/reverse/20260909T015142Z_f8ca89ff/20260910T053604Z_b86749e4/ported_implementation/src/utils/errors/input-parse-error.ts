import type { ValidInput } from '../../grammar-graph/types';
import { buildErrorPosition } from './build-error-position';
import { getInputAsString } from './get-input-as-string';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  private _mostRecentInput: ValidInput;
  private _pos: number;
  private _previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
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
    this.name = 'InputParseError';
    this._mostRecentInput = mostRecentInput;
    this._pos = pos;
    this._previousInput = previousInput;
  }

  public get pos(): number {
    return this._pos;
  }

  public get mostRecentInput(): ValidInput {
    return this._mostRecentInput;
  }

  public get previousInput(): ValidInput {
    return this._previousInput;
  }

  public get src(): string {
    return `${getInputAsString(this._previousInput)}${getInputAsString(this._mostRecentInput)}`;
  }

  public get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this._mostRecentInput), this._pos),
    ].join('\n');
  }
}
