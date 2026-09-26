import { at } from '../utils/code-points.ts';
import { GrammarParseError } from '../utils/errors/grammar-parse-error.ts';

const HEX = /^[0-9a-fA-F]+$/;

/**
 * A malformed escape would otherwise yield a `NaN` code point, which can never match
 * anything and silently poisons the grammar, so an explicit error is raised instead.
 */
const parseHex = (src: string[], pos: number, start: number, end: number): number => {
  const raw = src.slice(start, end).join('');
  if (!HEX.test(raw)) {
    throw new GrammarParseError(src.join(''), pos, `Invalid hex escape "${raw}"`);
  }
  return parseInt(raw, 16);
};

/** Returns the parsed code point, and how many positions it consumed. */
export const parseChar = (src: string[], pos: number): [number, number] => {
  if (at(src, pos) === '\\') {
    const next = at(src, pos + 1);
    switch (next) {
      case 'x':
        return [parseHex(src, pos, pos + 2, pos + 4), 4];
      case 'u':
        return [parseHex(src, pos, pos + 2, pos + 6), 6];
      case 'U':
        return [parseHex(src, pos, pos + 2, pos + 10), 10];
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
        return [src[pos + 1].codePointAt(0) as number, 2];
      default:
        throw new GrammarParseError(
          src.join(''),
          pos,
          `Unknown escape at ${at(src, pos)}`
        );
    }
  }

  if (!at(src, pos)) {
    throw new GrammarParseError(
      src.join(''),
      pos,
      'Unexpected end of grammar input, failed to complete parse'
    );
  }
  return [src[pos].codePointAt(0) as number, 1];
};
