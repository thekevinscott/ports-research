/** Port of `gbnf/utils/errors/input_parse_error.py`. */

import type { ValidInput } from '../../grammar-graph/types.js';
import { buildErrorPosition } from './build-error-position.js';
import { getInputAsString } from './get-input-as-string.js';

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = 'Failed to parse input string:';

export class InputParseError extends Error {
  #mostRecentInput: ValidInput;
  #pos: number;
  #previousInput: ValidInput;

  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    const previous = getInputAsString(previousInput);
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        '',
        ...buildErrorPosition(
          `${previous}${getInputAsString(mostRecentInput)}`,
          pos + previous.length,
        ),
      ].join('\n'),
    );
    Object.setPrototypeOf(this, InputParseError.prototype);
    this.name = 'InputParseError';
    this.#mostRecentInput = mostRecentInput;
    this.#pos = pos;
    this.#previousInput = previousInput;
  }

  get src(): string {
    return `${getInputAsString(this.#previousInput)}${getInputAsString(this.#mostRecentInput)}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      ...buildErrorPosition(getInputAsString(this.#mostRecentInput), this.#pos),
    ].join('\n');
  }
}
