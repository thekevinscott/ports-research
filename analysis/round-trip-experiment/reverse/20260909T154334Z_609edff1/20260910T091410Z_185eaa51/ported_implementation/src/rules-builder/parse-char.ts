import { charAt } from '../utils/char-at';
import { GrammarParseError } from '../utils/errors/grammar-parse-error';

/** Returns the parsed code point, and how many characters it consumed. */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const escaped = charAt(src, pos + 1);
    switch (escaped) {
      case 'x':
        return [parseInt(src.slice(pos + 2, pos + 4), 16), 4];
      case 'u':
        return [parseInt(src.slice(pos + 2, pos + 6), 16), 6];
      case 'U':
        return [parseInt(src.slice(pos + 2, pos + 10), 16), 10];
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
        throw new GrammarParseError(src, pos, `Unknown escape at ${charAt(src, pos)}`);
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
