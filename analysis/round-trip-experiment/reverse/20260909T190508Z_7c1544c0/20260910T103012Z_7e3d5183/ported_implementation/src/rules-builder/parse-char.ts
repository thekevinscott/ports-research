import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { charAt, codePointAt, slice } from '../utils/js.js';

const HEX_DIGITS = '0123456789abcdefABCDEF';

/**
 * `parseInt(src.slice(start, end), 16)`.
 *
 * A non-hex slice throws rather than yielding NaN, since a NaN code point
 * would silently produce an unmatchable rule.
 */
const parseHex = (src: string, pos: number, start: number, end: number): number => {
  const raw = slice(src, start, end);
  let digits = '';
  for (const char of raw) {
    if (HEX_DIGITS.includes(char)) {
      digits += char;
    } else {
      break;
    }
  }
  if (!digits) {
    throw new GrammarParseError(src, pos, `Invalid hex escape "${raw}"`);
  }
  return parseInt(digits, 16);
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const escape = charAt(src, pos + 1);
    if (escape === 'x') {
      return [parseHex(src, pos, pos + 2, pos + 4), 4];
    }
    if (escape === 'u') {
      return [parseHex(src, pos, pos + 2, pos + 6), 6];
    }
    if (escape === 'U') {
      return [parseHex(src, pos, pos + 2, pos + 10), 10];
    }
    if (escape === 't') {
      return ['\t'.codePointAt(0) as number, 2];
    }
    if (escape === 'r') {
      return ['\r'.codePointAt(0) as number, 2];
    }
    if (escape === 'n') {
      return ['\n'.codePointAt(0) as number, 2];
    }
    if (escape === '"' || escape === '[' || escape === ']') {
      return [codePointAt(src, pos + 1), 2];
    }
    if (escape === '\\') {
      return [codePointAt(src, pos + 1), 2];
    }
    throw new GrammarParseError(
      src,
      pos,
      `Unknown escape at ${charAt(src, pos)}`
    );
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [codePointAt(src, pos), 1];
};
