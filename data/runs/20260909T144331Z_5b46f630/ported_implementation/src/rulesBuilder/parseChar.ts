import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPE_CHARACTERS: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

const LITERAL_ESCAPES = ['"', '[', ']', '\\'];

const parseHex = (src: string, start: number, end: number, pos: number): number => {
  const hex = src.slice(start, end);
  if (hex.length !== end - start || !/^[0-9a-fA-F]+$/.test(hex)) {
    throw new GrammarParseError(src, pos, `Invalid hex escape at ${pos}`);
  }
  return parseInt(hex, 16);
};

/**
 * Parse a single character from the grammar, returning its code point along with the number of
 * characters consumed.
 */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }

  if (src[pos] === '\\') {
    const escaped = src[pos + 1];
    if (escaped === 'x') {
      return [parseHex(src, pos + 2, pos + 4, pos), 4];
    }
    if (escaped === 'u') {
      return [parseHex(src, pos + 2, pos + 6, pos), 6];
    }
    if (escaped === 'U') {
      return [parseHex(src, pos + 2, pos + 10, pos), 10];
    }
    if (escaped !== undefined && escaped in ESCAPE_CHARACTERS) {
      return [ESCAPE_CHARACTERS[escaped], 2];
    }
    if (escaped !== undefined && LITERAL_ESCAPES.includes(escaped)) {
      return [escaped.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  const codePoint = src.codePointAt(pos) as number;
  // a code point outside the basic multilingual plane occupies two UTF-16 code units
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};
