import { charAt } from '../utils/charAt.js';
import { GrammarParseError } from '../utils/errors/GrammarParseError.js';

const HEX_DIGITS = '0123456789abcdefABCDEF';
const LEADING_WHITESPACE = /^[ \t\n\r\f\v\u00a0]+/;

const parseHex = (
  src: string,
  pos: number,
  start: number,
  end: number,
  size: number,
): [number, number] => {
  // hex parsing skips leading whitespace, accepts a sign, and stops at the first
  // non-hex character rather than failing, so only that prefix is consumed
  let slice = src.slice(start, end).replace(LEADING_WHITESPACE, '');
  let sign = 1;
  if (slice[0] === '+' || slice[0] === '-') {
    sign = slice[0] === '-' ? -1 : 1;
    slice = slice.slice(1);
  }
  let digits = 0;
  while (digits < slice.length && HEX_DIGITS.includes(slice[digits])) {
    digits += 1;
  }
  if (digits === 0) {
    // nothing was parsed, which would build a rule that can never match
    throw new GrammarParseError(src, pos, `Invalid escape sequence "${src.slice(pos, end)}"`);
  }
  return [sign * parseInt(slice.slice(0, digits), 16), size];
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const escape = charAt(src, pos + 1);
    switch (escape) {
      case 'x':
        return parseHex(src, pos, pos + 2, pos + 4, 4);
      case 'u':
        return parseHex(src, pos, pos + 2, pos + 6, 6);
      case 'U':
        return parseHex(src, pos, pos + 2, pos + 10, 10);
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
        throw new GrammarParseError(src, pos, `Unknown escape at ${charAt(src, pos)}`);
    }
  }

  if (!charAt(src, pos)) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }
  return [src.codePointAt(pos) as number, 1];
};
