import { GrammarParseError } from '../utils/errors/grammar-parse-error';

export const PARSE_NAME_ERROR = 'Failed to find a valid name';

export const GET_INVALID_CHAR_ERROR = (char: string): string =>
  `Invalid character "${char}" when parsing name, only lowercase letters and hyphens are allowed.`;

const VALID_CHAR = /[a-zA-Z-]/;
const INVALID_NEXT_CHAR = /[_0-9]/;

const isValidChar = (char: string): boolean => VALID_CHAR.test(char);
const isInvalidNextChar = (char: string): boolean => INVALID_NEXT_CHAR.test(char);

export const parseName = (grammar: string, pos: number): string => {
  let name = '';
  while (pos < grammar.length && isValidChar(grammar[pos])) {
    name += grammar[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(grammar, pos, PARSE_NAME_ERROR);
  }
  if (pos < grammar.length && isInvalidNextChar(grammar[pos])) {
    throw new GrammarParseError(grammar, pos, GET_INVALID_CHAR_ERROR(grammar[pos]));
  }
  return name;
};
