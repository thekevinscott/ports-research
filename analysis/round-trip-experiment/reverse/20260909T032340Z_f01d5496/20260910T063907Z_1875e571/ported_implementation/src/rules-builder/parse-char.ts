import { GrammarParseError } from '../utils/errors/grammar-parse-error';

const at = (src: string, pos: number): string | undefined =>
  pos >= 0 && pos < src.length ? src[pos] : undefined;

const parseHex = (src: string, start: number, end: number): number =>
  parseInt(src.slice(start, end), 16);

export const parseChar = (src: string, pos: number): [number, number] => {
  if (at(src, pos) === '\\') {
    const escaped = at(src, pos + 1);
    switch (escaped) {
      case 'x':
        return [parseHex(src, pos + 2, pos + 4), 4];
      case 'u':
        return [parseHex(src, pos + 2, pos + 6), 6];
      case 'U':
        return [parseHex(src, pos + 2, pos + 10), 10];
      case 't':
        return ['\t'.codePointAt(0) as number, 2];
      case 'r':
        return ['\r'.codePointAt(0) as number, 2];
      case 'n':
        return ['\n'.codePointAt(0) as number, 2];
      case '"':
      case '[':
      case ']':
        return [src.codePointAt(pos + 1) as number, 2];
      case '\\': {
        const codePoint = at(src, pos + 1);
        if (codePoint === undefined) {
          throw new GrammarParseError(src, pos, 'Could not get code point for character');
        }
        return [codePoint.codePointAt(0) as number, 2];
      }
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (!at(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }
  return [src.codePointAt(pos) as number, 1];
};
