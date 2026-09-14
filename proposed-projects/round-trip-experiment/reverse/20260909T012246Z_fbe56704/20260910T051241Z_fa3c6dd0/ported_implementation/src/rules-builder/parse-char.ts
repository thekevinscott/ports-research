import { GrammarParseError } from '../utils/errors/grammar-parse-error.ts';
import { charAt } from './char-at.ts';

const parseHex = (src: string, pos: number, start: number, end: number): number => {
  const digits = src.slice(start, end);
  const value = parseInt(digits, 16);
  if (Number.isNaN(value)) {
    // an unparseable escape would otherwise be stored as an unmatchable code point;
    // failing loudly is more useful.
    throw new GrammarParseError(src, pos, `Invalid hex escape "${digits}"`);
  }
  return value;
};

/** Returns the code point at pos, and how far to advance past it. */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const escape = charAt(src, pos + 1);
    switch (escape) {
      case 'x':
        return [parseHex(src, pos, pos + 2, pos + 4), 4];
      case 'u':
        return [parseHex(src, pos, pos + 2, pos + 6), 6];
      case 'U':
        return [parseHex(src, pos, pos + 2, pos + 10), 10];
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
        return [escape.charCodeAt(0), 2];
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${charAt(src, pos)}`);
    }
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  const codePoint = src.codePointAt(pos) as number;
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};
