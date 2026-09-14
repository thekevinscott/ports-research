import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';

const parseHex = (src: string): number => {
  const value = parseInt(src, 16);
  if (Number.isNaN(value)) {
    throw new GrammarParseError(src, 0, `Could not parse hex value from ${src}`);
  }
  return value;
};

/** Returns the parsed code point, plus the number of characters it consumed. */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (src[pos] === '\\') {
    const escaped = src[pos + 1];
    switch (escaped) {
      case 'x':
        return [parseHex(src.substring(pos + 2, pos + 4)), 4];
      case 'u':
        return [parseHex(src.substring(pos + 2, pos + 6)), 6];
      case 'U':
        return [parseHex(src.substring(pos + 2, pos + 10)), 10];
      case 't':
        return ['\t'.codePointAt(0)!, 2];
      case 'r':
        return ['\r'.codePointAt(0)!, 2];
      case 'n':
        return ['\n'.codePointAt(0)!, 2];
      case '"':
      case '[':
      case ']':
      case '\\': {
        const codePoint = src.codePointAt(pos + 1);
        if (codePoint === undefined) {
          throw new GrammarParseError(
            src,
            pos,
            'Could not get code point for character'
          );
        }
        return [codePoint, 2];
      }
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  const codePoint = src.codePointAt(pos);
  if (codePoint === undefined) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [codePoint, 1];
};
