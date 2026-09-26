import { GrammarParseError } from '../utils/errors/index.js';
import { isWordChar } from './is-word-char.js';

export const PARSE_NAME_ERROR = 'Failed to find a valid name';

export const VALID_NAME_SEPARATORS = ['-', '_'];

export const parseName = (grammar: string, pos: number): string => {
  let name = '';
  while (
    pos < grammar.length &&
    (isWordChar(grammar[pos] as string) || VALID_NAME_SEPARATORS.includes(grammar[pos] as string))
  ) {
    name += grammar[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(grammar, pos, PARSE_NAME_ERROR);
  }
  return name;
};
