import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { charAt } from './parse-space.js';

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
        return ['\t'.codePointAt(0) as number, 2];
      case 'r':
        return ['\r'.codePointAt(0) as number, 2];
      case 'n':
        return ['\n'.codePointAt(0) as number, 2];
      case '"':
      case '[':
      case ']':
      case '\\':
        return [src.codePointAt(pos + 1) as number, 2];
      default:
        throw new GrammarParseError(
          src,
          pos,
          `Unknown escape at ${charAt(src, pos)}`
        );
    }
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [src.codePointAt(pos) as number, 1];
};
