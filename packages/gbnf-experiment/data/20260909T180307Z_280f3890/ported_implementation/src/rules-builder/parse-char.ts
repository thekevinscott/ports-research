import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPE_SEQUENCES: Record<string, number> = {
  t: 0x09,
  r: 0x0d,
  n: 0x0a,
  '"': 0x22,
  '[': 0x5b,
  ']': 0x5d,
  '\\': 0x5c,
};

const parseHex = (src: string, start: number, end: number, pos: number): number => {
  const hex = src.slice(start, end);
  const value = Number.parseInt(hex, 16);
  if (hex.length !== end - start || Number.isNaN(value)) {
    throw new GrammarParseError(src, pos, `Invalid escape sequence at ${pos}`);
  }
  return value;
};

/**
 * Parse a single (possibly escaped) character out of `src` at `pos`.
 *
 * Returns the code point along with the number of characters consumed.
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
    const next = src[pos + 1];
    if (next === 'x') {
      return [parseHex(src, pos + 2, pos + 4, pos), 4];
    }
    if (next === 'u') {
      return [parseHex(src, pos + 2, pos + 6, pos), 6];
    }
    if (next === 'U') {
      return [parseHex(src, pos + 2, pos + 10, pos), 10];
    }
    if (next !== undefined && next in ESCAPE_SEQUENCES) {
      return [ESCAPE_SEQUENCES[next] as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  const codePoint = src.codePointAt(pos) as number;
  // Surrogate pairs occupy two positions in a JS string, unlike in Python where
  // indexing is by code point.
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};
