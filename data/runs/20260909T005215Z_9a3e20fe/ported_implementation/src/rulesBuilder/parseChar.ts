import { GrammarParseError } from '../utils/errors/index.ts';

/** `int(<slice>, 16)` — throws on anything that is not a complete hex literal. */
const parseHex = (src: string, start: number, end: number): number => {
  const slice = src.slice(start, end);
  if (slice.length !== end - start || !/^[0-9a-fA-F]+$/u.test(slice)) {
    throw new Error(`invalid literal for int() with base 16: '${slice}'`);
  }
  return parseInt(slice, 16);
};

const SIMPLE_ESCAPES: Record<string, string> = {
  t: '\t',
  r: '\r',
  n: '\n',
};

const LITERAL_ESCAPES = ['"', '[', ']', '\\'];

/** Returns the parsed code point and the number of characters it consumed. */
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
      return [parseHex(src, pos + 2, pos + 4), 4];
    }
    if (next === 'u') {
      return [parseHex(src, pos + 2, pos + 6), 6];
    }
    if (next === 'U') {
      return [parseHex(src, pos + 2, pos + 10), 10];
    }
    if (next in SIMPLE_ESCAPES) {
      return [SIMPLE_ESCAPES[next].codePointAt(0) as number, 2];
    }
    if (LITERAL_ESCAPES.includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  // Python indexes strings by code point; JS by UTF-16 unit, so an astral
  // character occupies two positions here and has to advance `pos` by two.
  const codePoint = src.codePointAt(pos) as number;
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};
