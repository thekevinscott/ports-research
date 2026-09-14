import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { charAt, type Chars, fromChars, parseHex } from '../utils/js.js';

/** A parsed code point, and how many characters of source it consumed. */
export type ParsedChar = [codePoint: number, incPos: number];

const hex = (
  src: Chars,
  pos: number,
  start: number,
  end: number,
  width: number
): ParsedChar => {
  const value = parseHex(fromChars(src.slice(start, end)));
  if (value === undefined) {
    throw new GrammarParseError(fromChars(src), pos, `Unknown escape at ${charAt(src, pos)}`);
  }
  return [value, width];
};

export const parseChar = (src: Chars, pos: number): ParsedChar => {
  if (charAt(src, pos) === '\\') {
    const escape = charAt(src, pos + 1);
    switch (escape) {
      case 'x':
        return hex(src, pos, pos + 2, pos + 4, 4);
      case 'u':
        return hex(src, pos, pos + 2, pos + 6, 6);
      case 'U':
        return hex(src, pos, pos + 2, pos + 10, 10);
      case 't':
        return ['\t'.codePointAt(0) as number, 2];
      case 'r':
        return ['\r'.codePointAt(0) as number, 2];
      case 'n':
        return ['\n'.codePointAt(0) as number, 2];
      case '"':
      case '[':
      case ']':
        return [src[pos + 1].codePointAt(0) as number, 2];
      case '\\': {
        const codePoint = charAt(src, pos + 1);
        if (!codePoint) {
          throw new GrammarParseError(
            fromChars(src),
            pos,
            'Could not get code point for character'
          );
        }
        return [codePoint.codePointAt(0) as number, 2];
      }
      default:
        throw new GrammarParseError(
          fromChars(src),
          pos,
          `Unknown escape at ${charAt(src, pos)}`
        );
    }
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      fromChars(src),
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [src[pos].codePointAt(0) as number, 1];
};
