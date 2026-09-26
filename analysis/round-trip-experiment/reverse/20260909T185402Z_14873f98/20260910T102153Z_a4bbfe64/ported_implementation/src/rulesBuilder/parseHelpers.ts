import { GrammarParseError } from '../utils/errors/grammarParseError';

export const PARSE_NAME_ERROR = 'Failed to find a valid name';

export const GET_INVALID_CHAR_ERROR = (char: string): string =>
  `Invalid character "${char}" when parsing name, only lowercase letters and hyphens are allowed.`;

const WORD_CHAR = /[a-zA-Z]/;
const VALID_NAME_CHAR = /[a-zA-Z-]/;
const INVALID_NEXT_CHAR = /[_0-9]/;
const WHITESPACE = /\s/;

/** Reading out of bounds yields `undefined`. */
export const charAt = (src: string, pos: number): string | undefined =>
  src[pos];

export const isWordChar = (c?: string): boolean => !!c && WORD_CHAR.test(c);

export const isWhitespace = (c?: string): boolean => !!c && WHITESPACE.test(c);

export const parseName = (grammar: string, pos: number): string => {
  let name = '';
  while (pos < grammar.length && VALID_NAME_CHAR.test(grammar[pos])) {
    name += grammar[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(grammar, pos, PARSE_NAME_ERROR);
  }
  if (pos < grammar.length && INVALID_NEXT_CHAR.test(grammar[pos])) {
    throw new GrammarParseError(
      grammar,
      pos,
      GET_INVALID_CHAR_ERROR(grammar[pos]),
    );
  }
  return name;
};

export const parseSpace = (
  src: string,
  pos: number,
  newlineOk: boolean,
): number => {
  let char = charAt(src, pos);
  while (
    char === ' ' ||
    char === '\t' ||
    char === '#' ||
    (newlineOk && (char === '\r' || char === '\n'))
  ) {
    if (char === '#') {
      while (charAt(src, pos) && charAt(src, pos) !== '\r' && charAt(src, pos) !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
    char = charAt(src, pos);
  }
  return pos;
};

/** Returns the parsed code point, and the number of characters consumed. */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const escaped = charAt(src, pos + 1);
    switch (escaped) {
      case 'x':
        return [parseInt(src.substring(pos + 2, pos + 4), 16), 4];
      case 'u':
        return [parseInt(src.substring(pos + 2, pos + 6), 16), 6];
      case 'U':
        return [parseInt(src.substring(pos + 2, pos + 10), 16), 10];
      case 't':
        return ['\t'.charCodeAt(0), 2];
      case 'r':
        return ['\r'.charCodeAt(0), 2];
      case 'n':
        return ['\n'.charCodeAt(0), 2];
      case '"':
      case '[':
      case ']':
      case '\\':
        return [src.charCodeAt(pos + 1), 2];
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }
  return [src.charCodeAt(pos), 1];
};
