import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';

const HEX = /^[0-9a-fA-F]+$/;

const at = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

const parseHex = (src: string, pos: number, start: number, end: number) => {
  const slice = src.slice(start, end);
  if (!HEX.test(slice)) {
    throw new GrammarParseError(src, pos, `Invalid hex escape at ${pos}`);
  }
  return parseInt(slice, 16);
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (at(src, pos) === '\\') {
    const escape = at(src, pos + 1);
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
        return [src.charCodeAt(pos + 1), 2];
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
  return [src.charCodeAt(pos), 1];
};
