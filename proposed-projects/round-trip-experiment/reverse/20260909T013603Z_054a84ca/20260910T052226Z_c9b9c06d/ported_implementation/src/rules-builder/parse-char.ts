import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { parseHex } from '../utils/parse-hex.js';

const ESCAPE_WIDTHS: Record<string, number> = {
  x: 4,
  u: 6,
  U: 10,
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (src[pos] === '\\') {
    const escape = src[pos + 1];
    switch (escape) {
      case 'x':
      case 'u':
      case 'U': {
        const width = ESCAPE_WIDTHS[escape];
        const codePoint = parseHex(src.slice(pos + 2, pos + width));
        if (codePoint === undefined) {
          throw new GrammarParseError(src, pos, `Invalid escape at ${src[pos]}`);
        }
        return [codePoint, width];
      }
      case 't':
        return ['\t'.charCodeAt(0), 2];
      case 'r':
        return ['\r'.charCodeAt(0), 2];
      case 'n':
        return ['\n'.charCodeAt(0), 2];
      case '"':
      case '[':
      case ']':
        return [src.charCodeAt(pos + 1), 2];
      case '\\': {
        const codePoint = src[pos + 1];
        if (!codePoint) {
          throw new GrammarParseError(src, pos, 'Could not get code point for character');
        }
        return [codePoint.charCodeAt(0), 2];
      }
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (!src[pos]) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }
  return [src.charCodeAt(pos), 1];
};
