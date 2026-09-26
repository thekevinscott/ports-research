import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPED_CONTROL_CHARS: Record<string, number> = {
  t: '\t'.codePointAt(0)!,
  r: '\r'.codePointAt(0)!,
  n: '\n'.codePointAt(0)!,
};

const ESCAPED_LITERAL_CHARS = ['"', '[', ']', '\\'];

const parseHex = (raw: string): number => {
  if (!/^[0-9a-fA-F]+$/.test(raw)) {
    throw new Error(`Invalid hexadecimal escape sequence: "${raw}"`);
  }
  return parseInt(raw, 16);
};

/**
 * Parse a single character at `pos`, returning its code point along with the
 * number of characters consumed.
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
      return [parseHex(src.slice(pos + 2, pos + 4)), 4];
    }
    if (escaped === 'u') {
      return [parseHex(src.slice(pos + 2, pos + 6)), 6];
    }
    if (escaped === 'U') {
      return [parseHex(src.slice(pos + 2, pos + 10)), 10];
    }
    if (escaped in ESCAPED_CONTROL_CHARS) {
      return [ESCAPED_CONTROL_CHARS[escaped], 2];
    }
    if (ESCAPED_LITERAL_CHARS.includes(escaped)) {
      return [escaped.codePointAt(0)!, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  const codePoint = src.codePointAt(pos)!;
  return [codePoint, String.fromCodePoint(codePoint).length];
};
