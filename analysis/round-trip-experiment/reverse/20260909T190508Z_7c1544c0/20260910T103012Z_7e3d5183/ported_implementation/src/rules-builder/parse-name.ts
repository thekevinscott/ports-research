import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { codePoints } from '../utils/js.js';

export const PARSE_NAME_ERROR = 'Failed to find a valid name';

export const GET_INVALID_CHAR_ERROR = (char: string): string =>
  `Invalid character "${char}" when parsing name, ` +
  'only lowercase letters and hyphens are allowed.';

const VALID_CHAR = /[a-zA-Z-]/;
const INVALID_NEXT_CHAR = /[_0-9]/;

const isValidChar = (char: string): boolean => VALID_CHAR.test(char);

const isInvalidNextChar = (char: string): boolean => INVALID_NEXT_CHAR.test(char);

export const parseName = (grammar: string, pos: number): string => {
  const chars = codePoints(grammar);
  let name = '';
  while (pos < chars.length && isValidChar(chars[pos])) {
    name += chars[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(grammar, pos, PARSE_NAME_ERROR);
  }
  if (pos < chars.length && isInvalidNextChar(chars[pos])) {
    throw new GrammarParseError(
      grammar,
      pos,
      GET_INVALID_CHAR_ERROR(chars[pos])
    );
  }
  return name;
};
