/** Port of `gbnf/rules_builder/parse_char.py`. */

import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { charAt } from './char-at.js';

const HEX_DIGITS = '0123456789abcdefABCDEF';

/** Consume the leading hex digits of the slice, ignore the rest. */
const parseHex = (src: string, start: number, end: number, pos: number): number => {
  let digits = '';
  for (const char of src.slice(start, end)) {
    if (!HEX_DIGITS.includes(char)) {
      break;
    }
    digits += char;
  }
  if (!digits) {
    throw new GrammarParseError(src, pos, 'Could not parse hex escape');
  }
  return parseInt(digits, 16);
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (charAt(src, pos) === '\\') {
    const nextChar = charAt(src, pos + 1);
    switch (nextChar) {
      case 'x':
        return [parseHex(src, pos + 2, pos + 4, pos), 4];
      case 'u':
        return [parseHex(src, pos + 2, pos + 6, pos), 6];
      case 'U':
        return [parseHex(src, pos + 2, pos + 10, pos), 10];
      case 't':
        return ['\t'.charCodeAt(0), 2];
      case 'r':
        return ['\r'.charCodeAt(0), 2];
      case 'n':
        return ['\n'.charCodeAt(0), 2];
      case '"':
      case '[':
      case ']':
        return [nextChar.charCodeAt(0), 2];
      case '\\':
        return [nextChar.charCodeAt(0), 2];
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
  // A code point, not a UTF-16 unit, so an astral character is a single rule —
  // matching how input is decoded in `getInputAsCodePoints`. The cursor advances
  // by the character's width in UTF-16 units, since `src` is indexed that way.
  const codePoint = src.codePointAt(pos) as number;
  return [codePoint, String.fromCodePoint(codePoint).length];
};
