import { GrammarParseError } from '../utils/errors/grammarParseError.js';

const LEADING_HEX = /^[0-9a-fA-F]+/;

/** Mirror JS `parseInt(str, 16)`: consume the leading hex digits only. */
const parseHex = (src: string, start: number, end: number): number => {
  const match = LEADING_HEX.exec(src.slice(start, end));
  if (match === null) {
    throw new GrammarParseError(
      src,
      start,
      `Failed to parse hex escape at ${start}`
    );
  }
  return parseInt(match[0], 16);
};

const at = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

/** Returns the code point at `pos` and how far to advance past it. */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (at(src, pos) === '\\') {
    const escape = at(src, pos + 1);
    switch (escape) {
      case 'x':
        return [parseHex(src, pos + 2, pos + 4), 4];
      case 'u':
        return [parseHex(src, pos + 2, pos + 6), 6];
      case 'U':
        return [parseHex(src, pos + 2, pos + 10), 10];
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
        return [src.codePointAt(pos + 1) as number, 2];
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (!at(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  // the grammar is walked as code points, so an astral char advances two UTF-16 units
  const codePoint = src.codePointAt(pos) as number;
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};
