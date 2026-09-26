import { GrammarParseError } from '../utils/errors/grammar-parse-error';

export const parseChar = (src: string, pos: number): [number, number] => {
  if (src[pos] === '\\') {
    const nxt = src[pos + 1];
    switch (nxt) {
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
      case ']': {
        return [src[pos + 1].codePointAt(0) as number, 2];
      }
      case '\\': {
        const codePoint = src[pos + 1];
        if (codePoint === undefined) {
          throw new GrammarParseError(
            src,
            pos,
            'Could not get code point for character'
          );
        }
        return [codePoint.codePointAt(0) as number, 2];
      }
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (!src[pos]) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [src[pos].codePointAt(0) as number, 1];
};
